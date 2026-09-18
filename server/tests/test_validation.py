import pytest

from validation import MAX_MESSAGES, ApiError, clean_messages


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


def test_total_length_limit():
    twelve_k = [user("a" * 1000) if i % 2 == 0 else assistant("a" * 1000) for i in range(11)] + [user("a" * 1000)]
    assert len(clean_messages({"messages": twelve_k})) == 12

    assert error_code({"messages": [assistant("a" * 1000)] + twelve_k}) == "too_many_messages"


def test_keeps_only_the_last_messages():
    messages = [user(str(i)) if i % 2 == 0 else assistant(str(i)) for i in range(20)] + [user("last")]

    cleaned = clean_messages({"messages": messages})

    assert len(cleaned) == MAX_MESSAGES == 16
    assert cleaned[-1] == user("last")
    assert cleaned[0] == messages[-16]
