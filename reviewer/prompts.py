def build_review_prompt(code: str) -> str:
    return f"""
Review the following Python code.

Do not report issues that depend on assumptions about callers, undocumented
requirements, external context, or intended behavior.

A function returning None implicitly is not an issue unless the code clearly
requires a different return value.

Only report an issue when the code itself demonstrates a concrete failure,
security vulnerability, or incorrect behavior.

Security vulnerabilities may be reported when dangerous data flow is directly
visible in the code, even when the complete calling context is unavailable.

Return only valid JSON. Do not include Markdown fences, commentary, or text
before or after the JSON.

Use exactly this structure:

{{
  "issues": [
    {{
      "severity": "low | medium | high | critical",
      "category": "short category name",
      "title": "short issue title",
      "explanation": "why this is a real issue",
      "recommendation": "how to fix it"
    }}
  ]
}}

If no meaningful issues exist, return:

{{
  "issues": []
}}

Python code:

{code}
""".strip()
