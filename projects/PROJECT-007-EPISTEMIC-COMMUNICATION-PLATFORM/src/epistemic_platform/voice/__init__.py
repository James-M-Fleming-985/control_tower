"""Voice module — TTS, STT, composure analysis, and voice rendering."""

from epistemic_platform.voice.elevenlabs_tts import ElevenLabsTTSClient
from epistemic_platform.voice.protocol import PresentationRenderer, RenderResult
from epistemic_platform.voice.text_renderer import TextRenderer
from epistemic_platform.voice.voice_analyser import VocalState, VoiceAnalyser
from epistemic_platform.voice.voice_renderer import VoiceRenderer
from epistemic_platform.voice.whisper_stt import TranscriptionResult, WhisperSTTClient

__all__ = [
    "ElevenLabsTTSClient",
    "PresentationRenderer",
    "RenderResult",
    "TextRenderer",
    "TranscriptionResult",
    "VocalState",
    "VoiceAnalyser",
    "VoiceRenderer",
    "WhisperSTTClient",
]
