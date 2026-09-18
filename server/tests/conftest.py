import sys
from pathlib import Path

import functions_framework
import pytest

import llm

MAIN = Path(__file__).resolve().parent.parent / "main.py"
ALLOWED_ORIGIN = "https://badri-rajendran.github.io"
QUESTION = {"messages": [{"role": "user", "content": "What do you do?"}]}


@pytest.fixture
def app():
    """A fresh Functions Framework app; create_app reloads main.py, so limiters start empty."""
    return functions_framework.create_app(target="chat", source=str(MAIN))


@pytest.fixture
def main_module(app):
    return sys.modules["main"]


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def fake_reply(monkeypatch):
    """Replace the OpenAI call with a canned event sequence."""
    def install(events):
        def stream_reply(history):
            def generate():
                for item in events:
                    if isinstance(item, Exception):
                        raise item
                    yield item
            return generate()
        monkeypatch.setattr(llm, "stream_reply", stream_reply)
    install([("delta", {"t": "Hi, "}), ("delta", {"t": "I'm Badri."}), ("done", {"finish": "stop"})])
    return install


def post(client, body=QUESTION, origin=ALLOWED_ORIGIN, **kwargs):
    headers = {"Origin": origin} if origin else {}
    headers.update(kwargs.pop("headers", {}))
    return client.post("/", json=body, headers=headers, **kwargs)
