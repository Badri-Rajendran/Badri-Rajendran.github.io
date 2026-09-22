"""The only module that talks to OpenAI. Streams a reply as (event, data) pairs."""

import json
from collections.abc import Iterator

from openai import OpenAI, Timeout

from config import CONTACT_EMAIL, SETTINGS
from prompt import SYSTEM_PROMPT
from validation import ApiError

_client: OpenAI | None = None
# A stalled attempt fails over quickly; the worst case (3 x 15 s plus backoff) stays under
# the 60 s Cloud Run request timeout.
_TIMEOUT = Timeout(15.0, connect=5.0)
_MAX_RETRIES = 2


class UpstreamError(Exception):
    """OpenAI failed after the stream started."""


def _get_client() -> OpenAI:
    global _client
    if not SETTINGS.openai_api_key:
        raise ApiError("unavailable", 503, f"I'm offline right now. You can reach me at {CONTACT_EMAIL}.")
    if _client is None:
        _client = OpenAI(api_key=SETTINGS.openai_api_key, timeout=_TIMEOUT, max_retries=_MAX_RETRIES)
    return _client


def stream_reply(history: list[dict]) -> Iterator[tuple[str, dict]]:
    """Yield ("delta", {"t": text}) pairs, then ("done", {"finish": "stop" | "length"}).

    Raises ApiError immediately when unconfigured; raises UpstreamError while iterating.
    """
    return _events(_get_client(), history)


def _events(client: OpenAI, history: list[dict]) -> Iterator[tuple[str, dict]]:
    stream = client.responses.create(
        model=SETTINGS.openai_model,
        instructions=SYSTEM_PROMPT,
        input=history,
        reasoning={"effort": SETTINGS.reasoning_effort},
        text={"verbosity": "low"},
        max_output_tokens=SETTINGS.max_output_tokens,
        store=False,
        stream=True,
    )
    try:
        for event in stream:
            if event.type == "response.output_text.delta":
                yield "delta", {"t": event.delta}
            elif event.type == "response.completed":
                _log_usage(event.response.usage)
                yield "done", {"finish": "stop"}
                return
            elif event.type == "response.incomplete":
                _log_usage(event.response.usage)
                if event.response.incomplete_details.reason != "max_output_tokens":
                    raise UpstreamError(f"incomplete: {event.response.incomplete_details.reason}")
                yield "done", {"finish": "length"}
                return
            elif event.type == "response.failed":
                raise UpstreamError(f"failed: {event.response.error.message}")
            elif event.type == "error":
                raise UpstreamError(f"error: {event.message}")
        raise UpstreamError("stream ended without a final event")
    finally:
        stream.close()


def _log_usage(usage) -> None:
    """One structured log line per reply (token counts only, never message text)."""
    if usage is None:
        return
    print(json.dumps({
        "severity": "INFO",
        "message": "openai_usage",
        "input_tokens": usage.input_tokens,
        "cached_tokens": usage.input_tokens_details.cached_tokens,
        "output_tokens": usage.output_tokens,
    }), flush=True)
