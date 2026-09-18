from dataclasses import replace
from types import SimpleNamespace as NS

import pytest

import llm
from prompt import SYSTEM_PROMPT
from validation import ApiError

HISTORY = [{"role": "user", "content": "What do you do?"}]


def usage(cached=0):
    return NS(input_tokens=100, output_tokens=20, input_tokens_details=NS(cached_tokens=cached))


def delta(text):
    return NS(type="response.output_text.delta", delta=text)


def completed():
    return NS(type="response.completed", response=NS(usage=usage(cached=64)))


def incomplete(reason):
    return NS(type="response.incomplete", response=NS(incomplete_details=NS(reason=reason), usage=usage()))


class FakeStream:
    def __init__(self, events):
        self.events = events
        self.closed = False

    def __iter__(self):
        return iter(self.events)

    def close(self):
        self.closed = True


class FakeClient:
    def __init__(self, events):
        self.stream = FakeStream(events)
        self.kwargs = None
        self.responses = NS(create=self.create)

    def create(self, **kwargs):
        self.kwargs = kwargs
        return self.stream


@pytest.fixture
def fake_client(monkeypatch):
    def install(events):
        client = FakeClient(events)
        monkeypatch.setattr(llm, "_client", client)
        return client
    monkeypatch.setattr(llm, "SETTINGS", replace(llm.SETTINGS, openai_api_key="test-key"))
    return install


def test_maps_deltas_and_completion(fake_client):
    client = fake_client([delta("I'm "), NS(type="response.in_progress"), delta("Badri."), completed()])

    events = list(llm.stream_reply(HISTORY))

    assert events == [("delta", {"t": "I'm "}), ("delta", {"t": "Badri."}), ("done", {"finish": "stop"})]
    assert client.stream.closed


def test_sends_the_configured_request(fake_client):
    client = fake_client([completed()])

    list(llm.stream_reply(HISTORY))

    assert client.kwargs == {
        "model": "gpt-5-nano",
        "instructions": SYSTEM_PROMPT,
        "input": HISTORY,
        "reasoning": {"effort": "minimal"},
        "text": {"verbosity": "low"},
        "max_output_tokens": 725,
        "store": False,
        "stream": True,
    }


def test_output_cap_reports_length(fake_client):
    fake_client([delta("partial"), incomplete("max_output_tokens")])

    assert list(llm.stream_reply(HISTORY))[-1] == ("done", {"finish": "length"})


@pytest.mark.parametrize("events", [
    [incomplete("content_filter")],
    [NS(type="response.failed", response=NS(error=NS(message="boom")))],
    [NS(type="error", message="boom")],
    [delta("cut off")],  # stream ended without a terminal event
])
def test_upstream_failures_raise_and_close_the_stream(fake_client, events):
    client = fake_client(events)

    with pytest.raises(llm.UpstreamError):
        list(llm.stream_reply(HISTORY))
    assert client.stream.closed


def test_closing_early_closes_the_upstream_stream(fake_client):
    client = fake_client([delta("a"), delta("b"), completed()])

    events = llm.stream_reply(HISTORY)
    next(events)
    events.close()  # what happens when the visitor disconnects

    assert client.stream.closed


def test_missing_api_key_is_unavailable_before_streaming(monkeypatch):
    monkeypatch.setattr(llm, "SETTINGS", replace(llm.SETTINGS, openai_api_key=""))
    monkeypatch.setattr(llm, "_client", None)

    with pytest.raises(ApiError) as excinfo:
        llm.stream_reply(HISTORY)

    assert (excinfo.value.status, excinfo.value.code) == (503, "unavailable")


def test_logs_usage_without_message_text(fake_client, capsys):
    fake_client([delta("secret answer"), completed()])

    list(llm.stream_reply(HISTORY))

    log = capsys.readouterr().out
    assert '"cached_tokens": 64' in log
    assert "secret answer" not in log and "What do you do?" not in log
