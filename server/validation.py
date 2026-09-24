"""Request validation and the error type shared by every error response."""

MAX_MESSAGE_CHARS = 1_000   # per visitor message; see the role check in clean_messages
# Sized so MAX_MESSAGES is what actually ends a conversation: 16 turns of full-length
# replies land near this, and it stays inside MAX_BODY_BYTES in main.py.
MAX_TOTAL_CHARS = 24_000
MAX_MESSAGES = 16
ALLOWED_ROLES = ("user", "assistant")
CODE_FENCE = "```"


class ApiError(Exception):
    """An error returned to the client as {"error": {"code", "message"}} with an HTTP status."""

    def __init__(self, code: str, status: int, message: str, headers: dict | None = None):
        super().__init__(message)
        self.code = code
        self.status = status
        self.message = message
        self.headers = headers or {}


def _invalid(message: str) -> ApiError:
    return ApiError("invalid_request", 400, message)


def clean_messages(body) -> list[dict]:
    """Validate the request body and return the conversation as [{role, content}, ...]."""
    messages = body.get("messages") if isinstance(body, dict) else None
    if not isinstance(messages, list) or not messages:
        raise _invalid("Send a non-empty 'messages' list.")

    cleaned = []
    for message in messages:
        if not isinstance(message, dict) or message.get("role") not in ALLOWED_ROLES:
            raise _invalid("Each message needs a role of 'user' or 'assistant'.")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise _invalid("Each message needs non-empty text content.")
        if message["role"] == "user" and CODE_FENCE in content:
            # Matches the off-topic line in knowledge/persona.md: the same paste
            # refused by the model and by us should not sound like two people.
            raise ApiError("code_not_allowed", 400,
                           "I can only talk about my work and background. I don't review code here — "
                           "want to hear about PolicyPal or CodeSage?")
        # Only what the visitor typed. Assistant turns are our own replies echoed back for
        # context and routinely run past this cap, so applying it to them ended the
        # conversation the first time an answer ran long. MAX_TOTAL_CHARS still bounds a
        # forged one, as does MAX_BODY_BYTES.
        if message["role"] == "user" and len(content) > MAX_MESSAGE_CHARS:
            raise ApiError("message_too_long", 400, f"Messages are limited to {MAX_MESSAGE_CHARS} characters.")
        cleaned.append({"role": message["role"], "content": content.strip()})

    if sum(len(m["content"]) for m in cleaned) > MAX_TOTAL_CHARS:
        # The widget has no reset control, so don't ask for one.
        raise ApiError("too_many_messages", 400,
                       "We've covered a lot — reload the page to start a fresh conversation.")
    if cleaned[-1]["role"] != "user":
        raise _invalid("The last message must be from the user.")

    return cleaned[-MAX_MESSAGES:]
