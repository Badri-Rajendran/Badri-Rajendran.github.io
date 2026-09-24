import pytest

from validation import MAX_MESSAGES, MAX_TOTAL_CHARS, ApiError, clean_messages


def user(content):
    return {"role": "user", "content": content}


def assistant(content):
    return {"role": "assistant", "content": content}


def error_code(body):
    with pytest.raises(ApiError) as excinfo:
        clean_messages(body)
    assert excinfo.value.status == 400
    return excinfo.value.code


def test_returns_stripped_messages():
    body = {"messages": [user("  hi  "), assistant("hello"), user("What do you do?\n")]}

    assert clean_messages(body) == [user("hi"), assistant("hello"), user("What do you do?")]


def test_ignores_extra_fields_on_messages():
    assert clean_messages({"messages": [{"role": "user", "content": "hi", "name": "x"}]}) == [user("hi")]


@pytest.mark.parametrize("body", [
    None,
    [],
    "hi",
    {},
    {"messages": "hi"},
    {"messages": []},
    {"messages": ["hi"]},
    {"messages": [{"role": "user"}]},
    {"messages": [{"role": "user", "content": 42}]},
])
def test_rejects_malformed_bodies(body):
    assert error_code(body) == "invalid_request"


@pytest.mark.parametrize("role", ["system", "developer", "tool", "", None])
def test_rejects_roles_other_than_user_and_assistant(role):
    assert error_code({"messages": [{"role": role, "content": "hi"}]}) == "invalid_request"


def test_rejects_blank_content():
    assert error_code({"messages": [user("   \n ")]}) == "invalid_request"


def test_last_message_must_be_from_user():
    assert error_code({"messages": [user("hi"), assistant("hello")]}) == "invalid_request"


def test_rejects_fenced_code_in_user_messages():
    assert error_code({"messages": [user("Review this:\n```python\nprint(1)\n```")]}) == "code_not_allowed"


def test_allows_inline_backticks_and_fences_in_assistant_messages():
    body = {"messages": [user("What is `pgvector`?"), assistant("```"), user("Thanks")]}

    assert len(clean_messages(body)) == 3


def test_message_length_limit_is_inclusive():
    assert clean_messages({"messages": [user("a" * 1000)]}) == [user("a" * 1000)]
    assert error_code({"messages": [user("a" * 1001)]}) == "message_too_long"


def test_a_long_reply_does_not_block_the_next_question():
    """The cap is on what a visitor types, not on what the model said back.

    MAX_OUTPUT_TOKENS allows replies well past 1,000 characters, and the widget re-sends
    the whole conversation every turn. Capping assistant text too meant the first long
    answer killed the conversation: every later message, however short, came back
    "Messages are limited to 1000 characters." with no way out but a reload.
    """
    long_reply = "I built that at Zoho. " * 80   # 1,760 chars, a realistic answer length
    body = {"messages": [user("What did you build?"), assistant(long_reply), user("Tell me more.")]}

    cleaned = clean_messages(body)

    assert len(cleaned) == 3
    assert cleaned[1]["content"] == long_reply.strip()


def test_total_length_limit():
    """A backstop against a forged history, not something a real conversation reaches."""
    at_limit = [user("a" * 1000) if i % 2 == 0 else assistant("a" * 1000) for i in range(MAX_TOTAL_CHARS // 1000 - 1)]
    at_limit += [user("a" * 1000)]
    assert sum(len(m["content"]) for m in at_limit) == MAX_TOTAL_CHARS
    assert len(clean_messages({"messages": at_limit})) == MAX_MESSAGES

    assert error_code({"messages": [assistant("a" * 1000)] + at_limit}) == "too_many_messages"


def test_keeps_only_the_last_messages():
    messages = [user(str(i)) if i % 2 == 0 else assistant(str(i)) for i in range(20)] + [user("last")]

    cleaned = clean_messages({"messages": messages})

    assert len(cleaned) == MAX_MESSAGES == 16
    assert cleaned[-1] == user("last")
    assert cleaned[0] == messages[-16]
