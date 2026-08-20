from typing import Literal

Severity = Literal[
    "low",
    "medium",
    "high",
    "critical",
]

IssueCategory = Literal[
    "security",
    "bug",
    "performance",
    "maintainability",
]

IssueRule = Literal[
    "sql_injection",
    "shell_injection",
    "path_traversal",
    "unsafe_deserialization",
    "hardcoded_secret",
    "insecure_temp_file",
    "mutable_default_argument",
    "unreachable_code",
    "resource_leak",
    "broad_exception_handler",
    "missing_none_check",
    "duplicate_code",
    "long_function",
    "list_membership_in_loop",
    "string_concatenation_in_loop",
    "repeated_expensive_call_in_loop",
]

VALID_SEVERITIES: set[str] = {
    "low",
    "medium",
    "high",
    "critical",
}

VALID_CATEGORIES: set[str] = {
    "security",
    "bug",
    "performance",
    "maintainability",
}

VALID_RULES: set[str] = {
    "sql_injection",
    "shell_injection",
    "path_traversal",
    "unsafe_deserialization",
    "hardcoded_secret",
    "insecure_temp_file",
    "mutable_default_argument",
    "unreachable_code",
    "resource_leak",
    "broad_exception_handler",
    "missing_none_check",
    "duplicate_code",
    "long_function",
    "list_membership_in_loop",
    "string_concatenation_in_loop",
    "repeated_expensive_call_in_loop",
}

RULE_SEVERITY = {
    "duplicate_code": "medium",
    "list_membership_in_loop": "medium",
    "long_function": "low",
    "mutable_default_argument": "medium",
    "path_traversal": "high",
    "shell_injection": "critical",
    "sql_injection": "critical",
    "string_concatenation_in_loop": "low",
    "unreachable_code": "medium",
    "resource_leak": "medium",
    "broad_exception_handler": "medium",
    "missing_none_check": "medium",
    "unsafe_deserialization": "high",
    "hardcoded_secret": "high",
    "insecure_temp_file": "high",
    "repeated_expensive_call_in_loop": "medium",
}