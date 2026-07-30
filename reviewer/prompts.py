def build_review_prompt(source_code: str) -> str:
    return f"""
You are an expert Python code reviewer.

Review the Python code and report only meaningful issues.

Each issue must use one of these categories:

- security
- bug
- performance
- maintainability

Each issue must use one of these rules:

- sql_injection
- shell_injection
- path_traversal
- mutable_default_argument

Valid severity values:

- low
- medium
- high
- critical

Return only valid JSON using exactly this structure:

{{
  "issues": [
    {{
      "severity": "medium",
      "category": "bug",
      "rule": "mutable_default_argument",
      "title": "Mutable default argument",
      "explanation": "A mutable default value is shared between function calls.",
      "recommendation": "Use None as the default and create the object inside the function."
    }}
  ]
}}

If there are no meaningful issues, return:

{{
  "issues": []
}}

Do not return Markdown.
Do not use code fences.
Do not include any text before or after the JSON.

Python code:

{source_code}
"""