import pytest

from prompt import KNOWLEDGE_DIR, PRIVATE_HEADING, SYSTEM_PROMPT, build_system_prompt


def estimated_tokens(text):
    return len(text) / 4


def test_prompt_size_allows_caching_and_stays_small():
    assert 1_024 <= estimated_tokens(SYSTEM_PROMPT) <= 6_000


@pytest.mark.parametrize("fact", [
    "badriathindran@gmail.com",
    "+1 201-687-9279",
    "linkedin.com/in/badri-rajendran",
    "github.com/Badri-Rajendran",
    "GenAI Engineer Intern",
    "Presenter Prep",
    "PolicyPal",
    "CodeSage",
    "Trueup",
    "Lifeline",
    "Wipro",
    "Zoho Corporation",
    "Stevens Institute of Technology",
    "Anna University",
    "Open to Software Engineer (SDE), Full-Stack Engineer, Backend Engineer, Frontend Engineer, "
    "Cross-Platform Developer, GenAI Engineer, Forward Deployed Engineer roles",
])
def test_prompt_contains_key_facts(fact):
    assert fact in SYSTEM_PROMPT


def test_prompt_contains_rules_before_facts():
    assert SYSTEM_PROMPT.index("# How to respond") < SYSTEM_PROMPT.index("# Badri's background")


def test_prompt_mentions_no_retired_employer():
    assert "iNeuron" not in SYSTEM_PROMPT


def write_knowledge(directory, private=None):
    (directory / "persona.md").write_text("# How to respond\nrules\n")
    (directory / "badri.md").write_text("# Badri's background\nfacts\n")
    if private is not None:
        (directory / "private.md").write_text(private)


def test_private_facts_are_optional(tmp_path):
    write_knowledge(tmp_path)

    assert build_system_prompt(tmp_path) == "# How to respond\nrules\n\n# Badri's background\nfacts"


def test_private_facts_are_appended_under_a_heading(tmp_path):
    write_knowledge(tmp_path, private="Relocation: open to it.\n")

    prompt = build_system_prompt(tmp_path)

    assert prompt.endswith(f"{PRIVATE_HEADING}\n\nRelocation: open to it.")


def test_blank_private_file_is_ignored(tmp_path):
    write_knowledge(tmp_path, private="  \n")

    assert PRIVATE_HEADING not in build_system_prompt(tmp_path)


def test_knowledge_dir_has_required_files():
    assert (KNOWLEDGE_DIR / "persona.md").is_file()
    assert (KNOWLEDGE_DIR / "badri.md").is_file()
