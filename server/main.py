"""Badri.ai chat endpoint (Cloud Run function).

Handling order: CORS → method → body size → validation → rate limit → SSE stream.
"""

import json
import math

import functions_framework
from flask import Request, Response
from werkzeug.exceptions import RequestEntityTooLarge

import llm
from config import CONTACT_EMAIL, SETTINGS
from ratelimit import SlidingWindowLimiter
from sse import SSE_OPEN, sse
from validation import ApiError, clean_messages

MAX_BODY_BYTES = 32 * 1024
ALLOWED_METHODS = "GET, POST, OPTIONS"

PER_MINUTE = SlidingWindowLimiter(SETTINGS.rate_per_minute, 60)
PER_DAY = SlidingWindowLimiter(SETTINGS.rate_per_day, 86_400)
GLOBAL = SlidingWindowLimiter(SETTINGS.global_per_day, 86_400)


@functions_framework.http
def chat(request: Request) -> Response:
    origin = request.headers.get("Origin", "")
    cors = _cors_headers(origin)
    try:
        return _handle(request, origin, cors)
    except ApiError as err:
        return _json({"error": {"code": err.code, "message": err.message}}, err.status, {**cors, **err.headers},
                     streamed=err.status == 413)
    except Exception as exc:  # never leak internals to the visitor
        _log_error("server_error", exc)
        return _json({"error": {"code": "server_error", "message": "Something broke on my end. Please try again."}}, 500, cors)


def _handle(request: Request, origin: str, cors: dict) -> Response:
    if request.method == "GET":
        return _json({"ok": True}, 200, cors)
    if request.method not in ("POST", "OPTIONS"):
        raise ApiError("method_not_allowed", 405, "Use POST.", {"Allow": ALLOWED_METHODS})
    if origin not in SETTINGS.allowed_origins:
        raise ApiError("origin_not_allowed", 403, "This origin isn't allowed.")
    if request.method == "OPTIONS":
        return Response(status=204, headers={
            **cors,
            "Access-Control-Allow-Methods": ALLOWED_METHODS,
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600",
        })

    history = clean_messages(_read_json(request))
    _check_rate_limits(_client_ip(request))
    events = llm.stream_reply(history)

    def generate():
        yield SSE_OPEN
        try:
            for event, data in events:
                yield sse(event, data)
        except Exception as exc:
            _log_error("upstream_error", exc)
            yield sse("error", {"code": "upstream_error", "message": "I couldn't finish that answer. Please try again."})
        finally:
            events.close()  # runs on client disconnect too, so OpenAI stops generating

    return Response(generate(), mimetype="text/event-stream", headers={
        **cors,
        "Cache-Control": "no-cache, no-transform",
        "X-Accel-Buffering": "no",
    })


def _cors_headers(origin: str) -> dict:
    headers = {"Vary": "Origin"}
    if origin in SETTINGS.allowed_origins:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Expose-Headers"] = "Retry-After"
    return headers


def _read_json(request: Request):
    """Parse the JSON body (None if invalid). Reads at most one byte past MAX_BODY_BYTES, so
    oversized bodies get a 413 even when chunked with no Content-Length."""
    request.max_content_length = MAX_BODY_BYTES + 1
    try:
        data = request.get_data(cache=True)
    except RequestEntityTooLarge:  # Content-Length already over the limit
        data = None
    if data is None or len(data) > MAX_BODY_BYTES:
        raise ApiError("payload_too_large", 413, "That message is too large.")
    try:
        return json.loads(data)
    except ValueError:
        return None


def _client_ip(request: Request) -> str:
    """Google's front end appends the real client IP last; earlier entries can be spoofed."""
    forwarded = request.headers.get("X-Forwarded-For", "")
    return forwarded.split(",")[-1].strip() or request.remote_addr or "unknown"


def _check_rate_limits(ip: str) -> None:
    wait = PER_MINUTE.hit(ip)
    if wait:
        # The widget appends " Please try again in N s." from Retry-After,
        # so this must read as a complete sentence without saying that itself.
        raise ApiError("rate_limited", 429, "You're asking faster than I can answer.",
                       {"Retry-After": str(math.ceil(wait))})
    # No Retry-After on the daily cap: the honest value is 86400, and "try again in
    # 86400 s" is neither useful nor true to why they were stopped.
    if PER_DAY.hit(ip):
        raise ApiError("rate_limited", 429,
                       f"That's my limit of questions for today — you can email me at {CONTACT_EMAIL}.")
    if GLOBAL.hit("*"):
        raise ApiError("unavailable", 503, f"I've reached my daily chat limit. Please email me at {CONTACT_EMAIL}.")


def _json(payload: dict, status: int, headers: dict, streamed: bool = False) -> Response:
    """A JSON response. `streamed` stops the Functions Framework from buffering the rest of an
    oversized request body (its after_request hook reads the body for non-streamed responses)."""
    body = json.dumps(payload)
    return Response(iter([body]) if streamed else body, status=status, headers=headers, mimetype="application/json")


def _log_error(code: str, exc: Exception) -> None:
    print(json.dumps({"severity": "ERROR", "message": code, "error": f"{type(exc).__name__}: {exc}"}), flush=True)
