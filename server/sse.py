"""Server-sent event framing. Data is JSON so newlines in text can't break a frame."""

import json

# Comment frame sent first so headers reach the browser before the model's first token.
SSE_OPEN = ": ok\n\n"


def sse(event: str, data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return f"event: {event}\ndata: {payload}\n\n"
