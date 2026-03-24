"""Conversation manager — orchestrates a conversation session.

Coordinates between the context manager, prompt compositor, turn tracker,
LLM adapters, and the database to drive a complete conversation loop.
"""

from __future__ import annotations

import json
import logging
import re
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from epistemic_platform.engine.context_manager import ConversationContext, summarise_overflow
from epistemic_platform.engine.prompt_compositor import build_conversation_prompt
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

    @property
    def session_id(self) -> int:
        return self._session.id

    async def handle_user_message(
        self,
        user_text: str,
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
        await self._repo.append_message(
            self._session.id,
            {"role": "user", "content": user_text},
        )

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

        # 7. Record user turn and check coaching trigger
        self._turn_tracker.record_user_turn()

        await self._db.commit()

    async def maybe_run_coaching(self) -> CoachingAnnotation | None:
        """Check if coaching should trigger and run it if so.

        Returns CoachingAnnotation if coaching was run, None otherwise.
        """
        if self._turn_tracker.user_turn_count == 0:
            return None
        if self._turn_tracker.user_turn_count % self._turn_tracker._interval != 0:
            return None

        annotation = await self._turn_tracker.run_coaching_analysis(
            self._context.messages,
        )

        # Store coaching in DB
        await self._repo.append_coaching(
            self._session.id,
            annotation.to_dict(),
        )
        await self._db.commit()

        return annotation

    async def end_session(self) -> None:
        """End the conversation session."""
        await self._repo.end_session(self._session.id)
        await self._db.commit()

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
