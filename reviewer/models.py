from dataclasses import dataclass
from typing import Literal

Severity = Literal["low", "medium", "high", "critical"]


@dataclass
class Issue:
    severity:Severity
    category:str
    title:str
    explanation:str
    recommendation:str


@dataclass 
class CodeReview:
    issues: list[Issue]