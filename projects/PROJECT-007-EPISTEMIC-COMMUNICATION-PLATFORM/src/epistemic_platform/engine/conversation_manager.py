"""Conversation manager — orchestrates a conversation session.

Coordinates between the context manager, prompt compositor, turn tracker,
LLM adapters, trilemma tracker, horn detector, stance detector, and the
database to drive a complete conversation loop.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from epistemic_platform.config import get_settings
from epistemic_platform.engine.context_manager import ConversationContext, summarise_overflow
from epistemic_platform.engine.horn_detector import HornDetector, HornDetectionResult
from epistemic_platform.engine.prompt_compositor import build_conversation_prompt
from epistemic_platform.engine.stance_detector import StanceDetector, StanceDetectionResult, StanceHistory
from epistemic_platform.engine.trilemma_tracker import TrilemmaStateMachine, get_escape_strategy
from epistemic_platform.engine.turn_tracker import CoachingAnnotation, TurnTracker
from epistemic_platform.llm.protocol import CoachingLLM, EpistemicActorLLM, LLMStreamChunk
from epistemic_platform.models.actor_profile import ActorProfile
from epistemic_platform.models.conversation_session import ConversationSession
from epistemic_platform.ontology.actor_ontology import ActorOntology
from epistemic_platform.ontology.expressive_state import ExpressiveState
from epistemic_platform.repositories.conversation_session_repository import (
    ConversationSessionRepository,
)

logger = logging.getLogger(__name__)

# Regex to extract the |||META|||{...} line from the actor response
_META_PATTERN = re.compile(r"\|\|\|META\|\|\|(\{.*\})\s*$", re.DOTALL)


class ConversationManager:
    """Manages the lifecycle of a single conversation session."""

    def __init__(
        self,
        session: ConversationSession,
        actor: ActorProfile,
        conversation_llm: EpistemicActorLLM,
        coaching_llm: CoachingLLM,
        db: AsyncSession,
    ):
        self._session = session
        self._actor = actor
        self._db = db
        self._repo = ConversationSessionRepository(db)

        # Build ontology from actor config
        self._ontology = ActorOntology.from_config(actor.name, actor.ontology_config)

        # Build system prompt once (doesn't change mid-conversation)
        scenario = None
        if session.scenario:
            scenario = {
                "title": session.scenario.title,
                "description": session.scenario.description,
                "objectives": session.scenario.objectives or [],
                "evaluation_criteria": session.scenario.evaluation_criteria or [],
                "difficulty": session.scenario.difficulty,
                "category": session.scenario.category,
            }
        self._system_prompt = build_conversation_prompt(self._ontology, scenario=scenario)

        # Context window
        self._context = ConversationContext(
            messages=list(session.messages),
            summary="",
        )

        # Turn tracker for coaching triggers
        self._turn_tracker = TurnTracker(
            coaching_llm=coaching_llm,
            ontology=self._ontology,
        )
        # Restore turn count from session
        self._turn_tracker._user_turn_count = session.turn_count

        # LLM adapters
        self._conversation_llm = conversation_llm

        # M2: Trilemma state machine — restore from session or initialise
        self._trilemma = TrilemmaStateMachine.from_dict(session.trilemma_state or {})

        # M2: Horn detector — heuristics + optional LLM fallback
        settings = get_settings()
        self._horn_detector = HornDetector(
            llm=conversation_llm,
            llm_fallback=settings.horn_detection_llm_fallback,
        )

        # Last expressive state from actor response
        self._last_expressive_state: ExpressiveState | None = None

        # M2: Stance detector + history
        self._stance_detector = StanceDetector(conversation_llm)
        self._stance_history = StanceHistory.from_list(
            (session.trilemma_state or {}).get("stance_history", [])
        )
        self._stance_detection_interval = settings.stance_detection_interval

        # Last detection results (for WebSocket pushes)
        self._last_horn_result: HornDetectionResult | None = None
        self._last_stance_result: StanceDetectionResult | None = None

    @property
    def session_id(self) -> int:
        return self._session.id

    @property
    def last_expressive_state(self) -> ExpressiveState | None:
        """The ExpressiveState parsed from the most recent actor response."""
        return self._last_expressive_state

    async def handle_user_message(
        self,
        user_text: str,
        user_vocal_state: dict | None = None,
    ) -> AsyncIterator[LLMStreamChunk]:
        """Process a user message and yield streamed actor response chunks.

        Yields
        ------
        LLMStreamChunk
            Streamed text deltas from the conversation LLM.
            The final chunk has is_final=True.
        """
        # 1. Add user message to context + DB
        self._context.add_message("user", user_text)
        msg_data: dict[str, Any] = {"role": "user", "content": user_text}
        if user_vocal_state:
            msg_data["vocal_state"] = user_vocal_state
        await self._repo.append_message(self._session.id, msg_data)

        # 2. Summarise if context exceeds window
        await summarise_overflow(self._context, self._conversation_llm)

        # 3. Build LLM messages
        llm_messages = self._context.get_llm_messages()

        # 4. Stream actor response
        full_response = ""
        async for chunk in self._conversation_llm.generate_stream(
            messages=llm_messages,
            system_prompt=self._system_prompt,
        ):
            if chunk.delta:
                full_response += chunk.delta
            yield chunk

        # 5. Parse metadata from response
        clean_text, expressive_state = self._extract_metadata(full_response)
        self._last_expressive_state = expressive_state
        if expressive_state is None:
            logger.warning(
                "Session %d turn %d: actor response missing |||META||| metadata",
                self._session.id,
                self._turn_tracker.user_turn_count + 1,
            )

        # 6. Store the clean response in context + DB
        self._context.add_message("assistant", clean_text)
        await self._repo.append_message(
            self._session.id,
            {
                "role": "assistant",
                "content": clean_text,
                "expressive_state": expressive_state.__dict__ if expressive_state else None,
            },
        )

        # 7. Record user turn
        self._turn_tracker.record_user_turn()
        turn = self._turn_tracker.user_turn_count

        # 8. M2: Horn detection — run every turn (cheap heuristics)
        self._last_horn_result = await self._horn_detector.detect(self._context.messages)
        self._trilemma.detect_horn_and_transition(
            self._last_horn_result.horn,
            self._last_horn_result.confidence,
            turn,
        )

        # 9. M2: Stance detection — run every N turns
        if turn >= 2 and turn % self._stance_detection_interval == 0:
            self._last_stance_result = await self._stance_detector.detect(
                self._context.messages,
            )
            shifted = self._stance_history.record(turn, self._last_stance_result)
            if shifted:
                logger.info(
                    "Session %d: stance shift detected at turn %d → %s",
                    self._session.id, turn,
                    self._last_stance_result.stance.value if self._last_stance_result.stance else "unknown",
                )

        # 10. M2: Persist trilemma state + stance history to DB
        trilemma_dict = self._trilemma.to_dict()
        trilemma_dict["stance_history"] = self._stance_history.to_list()
        await self._repo.update_trilemma_state(self._session.id, trilemma_dict)

        await self._db.commit()

    async def maybe_run_coaching(self) -> CoachingAnnotation | None:
        """Check if coaching should trigger and run it if so.

        Returns CoachingAnnotation if coaching was run, None otherwise.
        """
        if self._turn_tracker.user_turn_count == 0:
            return None
        if self._turn_tracker.user_turn_count % self._turn_tracker._interval != 0:
            return None

        # M2: Pass trilemma and stance context to coaching
        latest_stance = self._stance_history.latest
        annotation = await self._turn_tracker.run_coaching_analysis(
            self._context.messages,
            trilemma_state=self._trilemma.to_dict(),
            detected_stance=latest_stance.stance.value if latest_stance else "",
            stance_confidence=latest_stance.confidence if latest_stance else 0.0,
        )

        # Store coaching in DB
        await self._repo.append_coaching(
            self._session.id,
            annotation.to_dict(),
        )
        await self._db.commit()

        return annotation

    def get_trilemma_state(self) -> dict[str, Any]:
        """Return the current trilemma state for WebSocket push."""
        return self._trilemma.to_dict()

    def get_last_horn_detection(self) -> dict[str, Any] | None:
        """Return the last horn detection result, if any."""
        if self._last_horn_result is None or self._last_horn_result.horn is None:
            return None
        return {
            "horn": self._last_horn_result.horn,
            "confidence": self._last_horn_result.confidence,
            "evidence": self._last_horn_result.evidence,
        }

    def get_last_stance_detection(self) -> dict[str, Any] | None:
        """Return the last stance detection result, if any."""
        if self._last_stance_result is None or self._last_stance_result.stance is None:
            return None
        return {
            "stance": self._last_stance_result.stance.value,
            "confidence": self._last_stance_result.confidence,
            "evidence": self._last_stance_result.evidence,
            "secondary_stance": (
                self._last_stance_result.secondary_stance.value
                if self._last_stance_result.secondary_stance
                else None
            ),
            "reasoning": self._last_stance_result.reasoning,
        }

    async def end_session(self, extra_metrics: dict | None = None) -> dict[str, Any]:
        """End the conversation session and compute outcome metrics.

        Parameters
        ----------
        extra_metrics : optional dict merged into the outcome (e.g. composure).

        Returns
        -------
        dict with session outcome metrics.
        """
        # Compute outcome metrics
        horn_visits = self._trilemma.horn_visits
        stance_snapshots = self._stance_history.snapshots
        unique_stances = {s.stance for s in stance_snapshots}

        # Check for stance shift: did the detected stance change during the session?
        stance_shift = len(unique_stances) > 1

        # Trilemma navigation score: how many horns were escaped vs visited
        total_visits = len(horn_visits)
        escaped_count = sum(1 for v in horn_visits if v.escaped)
        nav_score = escaped_count / total_visits if total_visits > 0 else 0.0

        # Check if any coaching annotations have gricean improvement
        coaching = self._session.coaching_annotations or []
        gricean_improvement = 0.0
        if len(coaching) >= 2:
            first_scores = coaching[0].get("gricean_scores", {})
            last_scores = coaching[-1].get("gricean_scores", {})
            if first_scores and last_scores:
                first_avg = sum(first_scores.values()) / max(len(first_scores), 1)
                last_avg = sum(last_scores.values()) / max(len(last_scores), 1)
                gricean_improvement = last_avg - first_avg

        outcome = {
            "stance_shift_detected": stance_shift,
            "unique_stances": [s.value for s in unique_stances],
            "trilemma_navigation_score": round(nav_score, 2),
            "horns_visited": total_visits,
            "horns_escaped": escaped_count,
            "gricean_improvement": round(gricean_improvement, 1),
            "total_turns": self._turn_tracker.user_turn_count,
            "coaching_count": len(coaching),
        }

        if extra_metrics:
            outcome.update(extra_metrics)

        # Persist outcome in trilemma_state alongside existing data
        trilemma_dict = self._trilemma.to_dict()
        trilemma_dict["stance_history"] = self._stance_history.to_list()
        trilemma_dict["session_outcome"] = outcome
        await self._repo.update_trilemma_state(self._session.id, trilemma_dict)

        await self._repo.end_session(self._session.id)
        await self._db.commit()

        return outcome

    def _extract_metadata(
        self, raw_response: str
    ) -> tuple[str, ExpressiveState | None]:
        """Extract |||META|||{...} from actor response, returning clean text + state."""
        match = _META_PATTERN.search(raw_response)
        if not match:
            return raw_response.strip(), None

        clean_text = raw_response[: match.start()].strip()
        try:
            meta = json.loads(match.group(1))
            state = ExpressiveState.from_llm_metadata(meta)
            return clean_text, state
        except (json.JSONDecodeError, KeyError, ValueError):
            return clean_text, None
