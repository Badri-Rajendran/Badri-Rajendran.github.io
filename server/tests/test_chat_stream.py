import io
import json

from conftest import ALLOWED_ORIGIN, post
from ratelimit import SlidingWindowLimiter
from validation import ApiError


def frames(response):
    return response.get_data(as_text=True).split("\n\n")[:-1]


def test_streams_open_comment_deltas_and_done(client, fake_reply):
    response = post(client)

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/event-stream; charset=utf-8"
    assert response.headers["Cache-Control"] == "no-cache, no-transform"
    assert response.headers["X-Accel-Buffering"] == "no"
    assert frames(response) == [
        ": ok",
        'event: delta\ndata: {"t":"Hi, "}',
        'event: delta\ndata: {"t":"I\'m Badri."}',
        'event: done\ndata: {"finish":"stop"}',
    ]


def test_upstream_failure_mid_stream_becomes_error_event(client, fake_reply, capsys):
    fake_reply([("delta", {"t": "Hi"}), RuntimeError("openai exploded")])

    last = frames(post(client))[-1]

    event, data = last.split("\n")
    assert event == "event: error"
    assert json.loads(data.removeprefix("data: "))["code"] == "upstream_error"
    assert "openai exploded" in capsys.readouterr().out  # logged for us, not sent to the visitor
    assert "openai exploded" not in last


def test_unconfigured_api_key_is_503_json(client, monkeypatch):
    import llm

    def unavailable(history):
        raise ApiError("unavailable", 503, "The assistant isn't available right now.")
    monkeypatch.setattr(llm, "stream_reply", unavailable)

    response = post(client)

    assert response.status_code == 503
    assert response.get_json()["error"]["code"] == "unavailable"


def test_health_check(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json() == {"ok": True}


def test_health_check_gets_cors_for_allowed_origin(client):
    response = client.get("/", headers={"Origin": ALLOWED_ORIGIN})

    assert response.headers["Access-Control-Allow-Origin"] == ALLOWED_ORIGIN


def test_other_methods_are_405(client):
    response = client.put("/", headers={"Origin": ALLOWED_ORIGIN})

    assert response.status_code == 405
    assert response.headers["Allow"] == "GET, POST, OPTIONS"
    assert response.get_json()["error"]["code"] == "method_not_allowed"


def test_oversized_body_is_413(client, fake_reply):
    body = {"messages": [{"role": "user", "content": "a" * 40_000}]}

    response = post(client, body=body)

    assert response.status_code == 413
    assert response.get_json()["error"]["code"] == "payload_too_large"


def test_oversized_chunked_body_without_content_length_is_413(client, fake_reply):
    body = json.dumps({"messages": [{"role": "user", "content": "a" * 40_000}]}).encode()

    response = client.post("/", input_stream=io.BytesIO(body), headers={
        "Origin": ALLOWED_ORIGIN, "Content-Type": "application/json", "Transfer-Encoding": "chunked",
    }, environ_overrides={"wsgi.input_terminated": True})  # what gunicorn sets for chunked bodies

    assert response.status_code == 413
    assert response.get_json()["error"]["code"] == "payload_too_large"


def test_body_of_exactly_the_limit_is_accepted(client, fake_reply, main_module):
    body = json.dumps({"messages": [{"role": "user", "content": "hi"}]})
    body += " " * (main_module.MAX_BODY_BYTES - len(body))  # trailing whitespace is valid JSON

    response = client.post("/", data=body, headers={"Origin": ALLOWED_ORIGIN, "Content-Type": "application/json"})

    assert response.status_code == 200


def test_invalid_json_is_400(client):
    response = client.post("/", data="not json", headers={"Origin": ALLOWED_ORIGIN, "Content-Type": "application/json"})

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "invalid_request"


def test_code_blocks_are_rejected(client, fake_reply):
    response = post(client, body={"messages": [{"role": "user", "content": "```\nprint(1)\n```"}]})

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "code_not_allowed"


def test_per_minute_limit_returns_429_with_retry_after(client, fake_reply):
    statuses = [post(client).status_code for _ in range(8)]
    limited = post(client)

    assert statuses == [200] * 8
    assert limited.status_code == 429
    assert 1 <= int(limited.headers["Retry-After"]) <= 60
    assert limited.get_json()["error"]["code"] == "rate_limited"


def test_limit_uses_last_forwarded_for_entry(client, fake_reply):
    def from_ip(real_ip, spoofed):
        return post(client, headers={"X-Forwarded-For": f"{spoofed}, {real_ip}"}).status_code

    assert [from_ip("203.0.113.7", f"10.0.0.{i}") for i in range(8)] == [200] * 8
    assert from_ip("203.0.113.7", "10.0.0.99") == 429  # spoofing the first entry doesn't help
    assert from_ip("198.51.100.1", "10.0.0.99") == 200


def test_invalid_requests_do_not_use_quota(client, fake_reply):
    for _ in range(10):
        post(client, body={"messages": []})

    assert post(client).status_code == 200


def test_global_daily_cap_returns_503(client, fake_reply, main_module):
    main_module.GLOBAL = SlidingWindowLimiter(limit=1, window_seconds=86_400)

    assert post(client).status_code == 200
    capped = post(client, headers={"X-Forwarded-For": "198.51.100.2"})
    assert capped.status_code == 503
    assert "badriathindran@gmail.com" in capped.get_json()["error"]["message"]
