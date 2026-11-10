"""LLM integration behind one interface (adapter pattern).

Providers:
  stub    — deterministic, offline; used in tests and CI
  ollama  — local model via http://localhost:11434 (no API key)
  openai  — any OpenAI-compatible /v1/chat/completions endpoint (needs LLM_API_KEY)

The prompt lives in a file (prompts/answer_v1.txt): prompt = configuration, not business logic.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Protocol

import httpx
from pydantic import BaseModel, Field, ValidationError

from assistant_core.errors import ProviderError
from assistant_core.rag.index import Hit

PROMPTS = Path(__file__).parent / "prompts"


class AnswerDraft(BaseModel):
    """The structured output we require from any LLM."""

    answer: str = Field(max_length=800)
    source_ids: list[str] = []
    confidence: float = Field(ge=0, le=1)
    abstain: bool = False


class LLM(Protocol):
    name: str

    def complete(self, prompt: str) -> str: ...


def build_prompt(question: str, hits: list[Hit], version: str = "answer_v1") -> str:
    template = (PROMPTS / f"{version}.txt").read_text(encoding="utf-8")
    sources = "\n".join(f"[{h.chunk.id}] {h.chunk.title}: {h.chunk.text}" for h in hits)
    return template.replace("{sources}", sources).replace("{question}", question)


def parse_draft(raw: str, allowed_ids: set[str]) -> AnswerDraft:
    """Validate the model output: JSON, schema, and grounding (only cite retrieved sources)."""
    m = re.search(r"\{.*\}", raw, flags=re.S)  # tolerate text around the JSON
    if not m:
        raise ProviderError("no JSON object in model output")
    try:
        draft = AnswerDraft.model_validate(json.loads(m.group(0)))
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ProviderError(f"invalid structured output: {type(exc).__name__}") from exc
    if not draft.abstain and (not draft.source_ids or not set(draft.source_ids) <= allowed_ids):
        raise ProviderError("answer cites sources that were not retrieved")
    return draft


class StubLLM:
    """Deterministic 'model': answers from the first source in the prompt. Good for tests and CI."""

    name = "stub"

    def __init__(self, fail: bool = False, garbage: bool = False):
        self.fail, self.garbage = fail, garbage

    def complete(self, prompt: str) -> str:
        if self.fail:
            raise ProviderError("stub provider unavailable")
        if self.garbage:
            return "Sure! Here is a great answer without any JSON."
        m = re.search(r"^\[([^\]]+)\] ([^:]+): (.+)$", prompt, flags=re.M)
        if not m:
            return json.dumps({"answer": "", "source_ids": [], "confidence": 0.0, "abstain": True})
        first_sentence = re.split(r"(?<=\.)\s", m.group(3))[0]
        return json.dumps(
            {
                "answer": f"According to {m.group(2)}: {first_sentence}",
                "source_ids": [m.group(1)],
                "confidence": 0.7,
                "abstain": False,
            }
        )


class OllamaLLM:
    name = "ollama"

    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434", timeout_s: float = 30):
        self.model, self.base_url = model, base_url.rstrip("/")
        self._http = httpx.Client(timeout=timeout_s)

    def complete(self, prompt: str) -> str:
        try:
            r = self._http.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "stream": False,
                    "format": "json",
                    "options": {"temperature": 0},
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            r.raise_for_status()
            return r.json()["message"]["content"]
        except (httpx.HTTPError, KeyError) as exc:
            raise ProviderError(f"ollama failed: {type(exc).__name__}") from exc


class OpenAICompatibleLLM:
    name = "openai"

    def __init__(self, api_key: str, model: str, base_url: str = "https://api.openai.com/v1", timeout_s: float = 20):
        self.model, self.base_url = model, base_url.rstrip("/")
        self._http = httpx.Client(timeout=timeout_s, headers={"Authorization": f"Bearer {api_key}"})

    def complete(self, prompt: str) -> str:
        try:
            r = self._http.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "temperature": 0,
                    "response_format": {"type": "json_object"},
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, IndexError) as exc:
            raise ProviderError(f"provider failed: {type(exc).__name__}") from exc


def make_llm(provider: str, model: str, base_url: str | None, api_key: str | None, timeout_s: float) -> LLM:
    if provider == "stub":
        return StubLLM()
    if provider == "ollama":
        return OllamaLLM(model, base_url or "http://localhost:11434", timeout_s)
    if provider == "openai":
        if not api_key:
            raise ProviderError("LLM_API_KEY required for provider 'openai'")
        return OpenAICompatibleLLM(api_key, model, base_url or "https://api.openai.com/v1", timeout_s)
    raise ProviderError(f"unknown LLM provider {provider!r}")
