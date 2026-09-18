import json

from sse import SSE_OPEN, sse


def test_frames_event_with_json_data():
    assert sse("done", {"finish": "stop"}) == 'event: done\ndata: {"finish":"stop"}\n\n'


def test_newlines_in_text_stay_inside_one_data_line():
    frame = sse("delta", {"t": "line one\n\nline two"})

    event_line, data_line, *rest = frame.split("\n")
    assert event_line == "event: delta"
    assert json.loads(data_line.removeprefix("data: ")) == {"t": "line one\n\nline two"}
    assert rest == ["", ""]


def test_non_ascii_is_kept_readable():
    assert "é" in sse("delta", {"t": "résumé"})


def test_open_frame_is_a_comment():
    assert SSE_OPEN == ": ok\n\n"
