"""Deterministic guardrails that run BEFORE retrieval or any LLM call."""

from __future__ import annotations

import re

PRIVATE_PATTERNS = [
    r"\b(my|a) (friend|classmate|roommate)'?s?\b.*\b(grade|score|gpa|result|phone|address)",
    r"\b(grade|score|gpa|result|phone|address)s?\b.*\b(of|for) (another|other) student",
    r"\b(grade|score|gpa|result|phone|address)s?\b.*\b(my|a) (friend|classmate|roommate)",
    r"\b\d{8}\b",  # looks like a student id
]


def is_private_request(text: str) -> bool:
    t = text.lower()
    return any(re.search(p, t) for p in PRIVATE_PATTERNS)


PRIVATE_REPLY = "I can't share information about other students. You can only see your own records after logging in."
