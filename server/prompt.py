"""Builds the system prompt from the Markdown files in knowledge/.

The prompt is built once at import and never varies per request, so OpenAI's
automatic prompt caching can reuse it.
"""

from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"
PRIVATE_HEADING = "# Additional facts"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip() if path.is_file() else ""


def build_system_prompt(knowledge_dir: Path = KNOWLEDGE_DIR) -> str:
    sections = [_read(knowledge_dir / "persona.md"), _read(knowledge_dir / "badri.md")]
    private = _read(knowledge_dir / "private.md")
    if private:
        sections.append(f"{PRIVATE_HEADING}\n\n{private}")
    return "\n\n".join(sections)


SYSTEM_PROMPT = build_system_prompt()
