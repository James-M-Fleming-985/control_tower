"""Voice analyser — extracts composure metrics from user audio.

Runs librosa-based prosody analysis in a thread pool to avoid blocking
the event loop. Falls back gracefully when librosa is not installed.
"""

from __future__ import annotations

import asyncio
import io
import logging
from dataclasses import asdict, dataclass

logger = logging.getLogger(__name__)

try:
    import librosa
    import numpy as np

    _HAS_LIBROSA = True
except ImportError:
    _HAS_LIBROSA = False
    logger.info("librosa not available — voice composure analysis disabled")


@dataclass
class VocalState:
    """Prosody metrics extracted from a user's audio."""

    pitch_variability: float  # Coefficient of variation of F0 (0 = monotone)
    volume_stability: float  # 0-1, higher = more stable RMS energy
    jitter: float  # Mean absolute F0 perturbation between consecutive frames
    speaking_rate_wpm: float  # Words per minute (set externally from STT)
    composure_score: float  # 0-1, weighted composite (higher = more composed)

    def to_dict(self) -> dict:
        return asdict(self)


class VoiceAnalyser:
    """Extracts vocal composure metrics from audio using librosa."""

    @staticmethod
    def available() -> bool:
        return _HAS_LIBROSA

    async def analyse(
        self,
        audio_bytes: bytes,
        word_count: int | None = None,
        sample_rate: int = 16000,
    ) -> VocalState | None:
        """Analyse audio bytes and return VocalState.

        Parameters
        ----------
        audio_bytes : raw audio data (WAV, WebM, MP3 — requires ffmpeg for compressed)
        word_count : transcription word count (for speaking rate)
        sample_rate : target sample rate for analysis
        """
        if not _HAS_LIBROSA:
            return None

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, self._analyse_sync, audio_bytes, word_count, sample_rate
        )

    def _analyse_sync(
        self,
        audio_bytes: bytes,
        word_count: int | None,
        sample_rate: int,
    ) -> VocalState | None:
        try:
            y, sr = librosa.load(io.BytesIO(audio_bytes), sr=sample_rate, mono=True)
            duration = len(y) / sr
            if duration < 0.5:
                logger.debug("Audio too short (%.1fs) for composure analysis", duration)
                return None

            # --- Pitch (F0) via pYIN ---
            f0, voiced_flag, _ = librosa.pyin(
                y,
                fmin=librosa.note_to_hz("C2"),
                fmax=librosa.note_to_hz("C7"),
                sr=sr,
            )
            voiced_f0 = f0[~np.isnan(f0)]

            if len(voiced_f0) < 2:
                pitch_cv = 0.0
                jitter_val = 0.0
            else:
                mean_f0 = float(np.mean(voiced_f0))
                pitch_cv = float(np.std(voiced_f0) / mean_f0) if mean_f0 > 0 else 0.0
                jitter_val = (
                    float(np.mean(np.abs(np.diff(voiced_f0))) / mean_f0)
                    if mean_f0 > 0
                    else 0.0
                )

            # --- Volume stability (RMS energy) ---
            rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]
            mean_rms = float(np.mean(rms))
            volume_stability = (
                float(1.0 - min(1.0, np.std(rms) / mean_rms))
                if mean_rms > 0
                else 0.5
            )

            # --- Speaking rate ---
            speaking_rate_wpm = 0.0
            if word_count is not None and duration > 0:
                speaking_rate_wpm = (word_count / duration) * 60.0

            # --- Composure score ---
            pitch_score = max(0.0, 1.0 - pitch_cv * 2.0)
            jitter_score = max(0.0, 1.0 - jitter_val * 10.0)
            volume_score = volume_stability

            if speaking_rate_wpm > 0:
                rate_deviation = abs(speaking_rate_wpm - 140.0) / 140.0
                rate_score = max(0.0, 1.0 - rate_deviation)
            else:
                rate_score = 0.5

            composure = (
                0.35 * pitch_score
                + 0.25 * jitter_score
                + 0.25 * volume_score
                + 0.15 * rate_score
            )

            return VocalState(
                pitch_variability=round(pitch_cv, 4),
                volume_stability=round(volume_stability, 4),
                jitter=round(jitter_val, 4),
                speaking_rate_wpm=round(speaking_rate_wpm, 1),
                composure_score=round(min(1.0, max(0.0, composure)), 4),
            )

        except Exception:
            logger.exception("Voice analysis failed")
            return None
