from pathlib import Path


PROMPTS_DIRECTORY = Path("prompts")
SOURCE_CODE_PLACEHOLDER = "{{SOURCE_CODE}}"
DEFAULT_PROMPT_VERSION = "v1"
REVIEW_PROMPT_TYPE = "review"


def load_prompt_template(
    prompt_version: str,
    prompt_type: str,
) -> str:
    """Load a versioned prompt template."""

    prompt_path = (
        PROMPTS_DIRECTORY
        / prompt_version
        / f"{prompt_type}.txt"
    )

    if not prompt_path.is_file():
        raise ValueError(
            f"Prompt template not found: "
            f"{prompt_version}/{prompt_type}"
        )

    return prompt_path.read_text(encoding="utf-8")


def build_review_prompt(
    source_code: str,
    prompt_version: str = DEFAULT_PROMPT_VERSION,
) -> str:
    """Build a code-review prompt from a versioned template."""

    template = load_prompt_template(
        prompt_version=prompt_version,
        prompt_type=REVIEW_PROMPT_TYPE,
    )

    if SOURCE_CODE_PLACEHOLDER not in template:
        raise ValueError(
            "Prompt template is missing: "
            f"{SOURCE_CODE_PLACEHOLDER}"
        )

    return template.replace(
        SOURCE_CODE_PLACEHOLDER,
        source_code,
    )