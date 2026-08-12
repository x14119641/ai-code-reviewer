from pathlib import Path

PROMPTS_DIRECTORY = Path("prompts")
SOURCE_CODE_PLACEHOLDER = "{{SOURCE_CODE}}"
DIFF_PLACEHOLDER = "{{DIFF}}"
CURRENT_CODE_PLACEHOLDER = "{{CURRENT_CODE}}"

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
    prompt_version: str,
    prompt_type: str,
    replacements: dict[str, str],
) -> str:
    template = load_prompt_template(
        prompt_version=prompt_version,
        prompt_type=prompt_type,
    )

    for placeholder, content in replacements.items():
        if placeholder not in template:
            raise ValueError(f"Prompt template is missing: {placeholder}")

        template = template.replace(
            placeholder,
            content,
        )

    return template


def build_review_prompt(
    source_code: str,
    prompt_version: str = DEFAULT_PROMPT_VERSION,
) -> str:
    """Build a code-review prompt from a versioned template."""
    return _build_prompt(
        prompt_version=prompt_version,
        prompt_type=REVIEW_PROMPT_TYPE,
        replacements={
            SOURCE_CODE_PLACEHOLDER: source_code,
        },
    )


def build_diff_prompt(
    diff: str,
    current_code: str,
    prompt_version: str = DEFAULT_PROMPT_VERSION,
) -> str:
    """Build a Git diff review prompt from a versioned template."""
    return _build_prompt(
        prompt_version=prompt_version,
        prompt_type=DIFF_PROMPT_TYPE,
        replacements={
            DIFF_PLACEHOLDER: diff,
            CURRENT_CODE_PLACEHOLDER: current_code,
        },
    )
