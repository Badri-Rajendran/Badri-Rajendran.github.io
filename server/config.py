"""Runtime settings, read once from environment variables (see env.yaml)."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_model: str
    reasoning_effort: str
    max_output_tokens: int
    allowed_origins: tuple[str, ...]
    rate_per_minute: int
    rate_per_day: int
    global_per_day: int


def load_settings() -> Settings:
    env = os.environ.get
    return Settings(
        openai_api_key=env("OPENAI_API_KEY", ""),
        openai_model=env("OPENAI_MODEL", "gpt-5-nano"),
        reasoning_effort=env("REASONING_EFFORT", "minimal"),
        max_output_tokens=int(env("MAX_OUTPUT_TOKENS", "725")),
        allowed_origins=tuple(
            origin.strip()
            for origin in env(
                "ALLOWED_ORIGINS",
                "https://badri-rajendran.github.io,http://localhost:8000",
            ).split(",")
            if origin.strip()
        ),
        rate_per_minute=int(env("RATE_PER_MINUTE", "8")),
        rate_per_day=int(env("RATE_PER_DAY", "60")),
        global_per_day=int(env("GLOBAL_PER_DAY", "1500")),
    )


SETTINGS = load_settings()
