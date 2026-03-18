from pydantic import field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # App
    app_name: str = "Epistemic Communication Platform"
    debug: bool = False
    api_prefix: str = "/api"
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/epistemic_platform"

    @field_validator("database_url", mode="before")
    @classmethod
    def ensure_async_scheme(cls, v: str) -> str:
        # Strip whitespace and any trailing garbage characters that can
        # appear from misconfigured Railway variable references.
        v = v.strip().rstrip(")")
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    # Auth
    secret_key: str = "change-this-in-production-minimum-32-characters-long"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Claude (Anthropic)
    anthropic_api_key: str = ""
    claude_sonnet_model: str = "claude-sonnet-4-20250514"
    claude_opus_model: str = "claude-opus-4-20250514"
    claude_conversation_temperature: float = 0.7
    claude_coaching_temperature: float = 0.4
    claude_max_tokens: int = 4096

    # OpenAI (Whisper STT)
    openai_api_key: str = ""
    whisper_model: str = "whisper-1"

    # ElevenLabs (TTS)
    elevenlabs_api_key: str = ""
    elevenlabs_default_voice_id: str = ""
    elevenlabs_model_id: str = "eleven_multilingual_v2"

    # Conversation
    context_window_max_messages: int = 20
    coaching_trigger_interval: int = 4
    max_concurrent_sessions: int = 50

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
