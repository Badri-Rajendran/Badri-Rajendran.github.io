import pytest

from conftest import ALLOWED_ORIGIN, post


def test_preflight_from_allowed_origin(client):
    response = client.options("/", headers={"Origin": ALLOWED_ORIGIN, "Access-Control-Request-Method": "POST"})

    assert response.status_code == 204
    assert response.headers["Access-Control-Allow-Origin"] == ALLOWED_ORIGIN
    assert response.headers["Access-Control-Allow-Methods"] == "GET, POST, OPTIONS"
    assert response.headers["Access-Control-Allow-Headers"] == "Content-Type"
    assert response.headers["Access-Control-Max-Age"] == "3600"
    assert response.headers["Vary"] == "Origin"


def test_localhost_is_allowed_for_development(client):
    response = client.options("/", headers={"Origin": "http://localhost:8000"})

    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:8000"


def test_preflight_from_other_origin_is_forbidden(client):
    response = client.options("/", headers={"Origin": "https://evil.example"})

    assert response.status_code == 403
    assert "Access-Control-Allow-Origin" not in response.headers


@pytest.mark.parametrize("origin", ["https://evil.example", None])
def test_post_from_other_or_missing_origin_is_forbidden(client, fake_reply, origin):
    response = post(client, origin=origin)

    assert response.status_code == 403
    assert response.get_json() == {"error": {"code": "origin_not_allowed", "message": "This origin isn't allowed."}}


def test_cors_headers_are_on_error_responses(client):
    response = post(client, body={"messages": []})

    assert response.status_code == 400
    assert response.headers["Access-Control-Allow-Origin"] == ALLOWED_ORIGIN
    assert response.headers["Access-Control-Expose-Headers"] == "Retry-After"


def test_cors_headers_are_on_the_stream(client, fake_reply):
    response = post(client)

    assert response.headers["Access-Control-Allow-Origin"] == ALLOWED_ORIGIN
    assert response.headers["Vary"] == "Origin"
