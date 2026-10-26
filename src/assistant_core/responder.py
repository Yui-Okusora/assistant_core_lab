"""Response generation behind one interface (adapter pattern)."""

from __future__ import annotations

from typing import Protocol

from assistant_core.errors import ProviderError
from assistant_core.knowledge import Rule


class Responder(Protocol):
    def explain(self, question: str, rule: Rule) -> str: ...


class TemplateResponder:
    """No AI: quote the rule. Always available — also used as the fallback."""

    def explain(self, question: str, rule: Rule) -> str:
        return f"{rule.title}: {rule.text}"


class StubLLMResponder:
    """Stands in for a real LLM until Week 4. `fail=True` simulates an outage in tests."""

    def __init__(self, fail: bool = False):
        self.fail = fail

    def explain(self, question: str, rule: Rule) -> str:
        if self.fail:
            raise ProviderError("stub provider unavailable")
        return f"Based on '{rule.title}': {rule.text}"


def make_responder(provider: str) -> Responder:
    if provider == "stub":
        return StubLLMResponder()
    if provider == "template":
        return TemplateResponder()
    raise ProviderError(f"unknown provider {provider!r} (real providers arrive in Week 4)")
