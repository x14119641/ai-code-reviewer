from pathlib import Path

PROMPTS_DIRECTORY = Path("prompts")
SOURCE_CODE_PLACEHOLDER = "{{SOURCE_CODE}}"
DIFF_PLACEHOLDER = "{{DIFF}}"

DEFAULT_PROMPT_VERSION = "v6"

REVIEW_PROMPT_TYPE = "review"
DIFF_PROMPT_TYPE = "diff"


def load_prompt_template(
    prompt_version: str,
    prompt_type: str,
) -> str:
    """Load a versioned prompt template."""

    prompt_path = PROMPTS_DIRECTORY / prompt_version / f"{prompt_type}.txt"

    if not prompt_path.is_file():
        raise ValueError(
            f"Prompt template not found: " f"{prompt_version}/{prompt_type}"
        )

    return prompt_path.read_text(encoding="utf-8")


def _build_prompt(
    content: str,
    prompt_version: str,
    prompt_type: str,
    placeholder: str,
) -> str:
    template = load_prompt_template(
        prompt_version=prompt_version,
        prompt_type=prompt_type,
    )

    if placeholder not in template:
        raise ValueError(f"Prompt template is missing: {placeholder}")

    return template.replace(
        placeholder,
        content,
    )


def build_review_prompt(
    source_code: str,
    prompt_version: str = DEFAULT_PROMPT_VERSION,
) -> str:
    """Build a code-review prompt from a versioned template."""
    return _build_prompt(
        content=source_code,
        prompt_version=prompt_version,
        prompt_type=REVIEW_PROMPT_TYPE,
        placeholder=SOURCE_CODE_PLACEHOLDER,
    )


def build_diff_prompt(
    diff: str,
    prompt_version: str = DEFAULT_PROMPT_VERSION,
) -> str:
    """Build a Git diff review prompt from a versioned template."""
    return _build_prompt(
        content=diff,
        prompt_version=prompt_version,
        prompt_type=DIFF_PROMPT_TYPE,
        placeholder=DIFF_PLACEHOLDER,
    )
