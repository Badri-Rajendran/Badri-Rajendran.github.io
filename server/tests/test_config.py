from config import load_settings


def test_defaults_match_spec(monkeypatch):
    for name in ("OPENAI_API_KEY", "OPENAI_MODEL", "REASONING_EFFORT", "MAX_OUTPUT_TOKENS",
                 "ALLOWED_ORIGINS", "RATE_PER_MINUTE", "RATE_PER_DAY", "GLOBAL_PER_DAY"):
        monkeypatch.delenv(name, raising=False)

    settings = load_settings()

    assert settings.openai_api_key == ""
    assert settings.openai_model == "gpt-5-nano"
    assert settings.reasoning_effort == "minimal"
    assert settings.max_output_tokens == 725
    assert settings.allowed_origins == ("https://badri-rajendran.github.io", "http://localhost:8000")
    assert (settings.rate_per_minute, settings.rate_per_day, settings.global_per_day) == (8, 60, 1500)


def test_allowed_origins_are_trimmed_and_blank_entries_dropped(monkeypatch):
    monkeypatch.setenv("ALLOWED_ORIGINS", " https://a.example , ,http://localhost:8000 ")

    assert load_settings().allowed_origins == ("https://a.example", "http://localhost:8000")
