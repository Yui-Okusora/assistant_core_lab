"""Knowledge sources: office directory (structured) and handbook rules (documents)."""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path

from assistant_core.errors import DataError


@dataclass(frozen=True)
class Office:
    name: str
    room: str
    hours: str


@dataclass(frozen=True)
class Rule:
    id: str
    title: str
    text: str


class OfficeDirectory:
    def __init__(self, offices: dict[str, Office]):
        self._offices = offices

    @classmethod
    def from_csv(cls, path: Path) -> OfficeDirectory:
        try:
            with path.open(encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
        except FileNotFoundError as exc:
            raise DataError(f"office file not found: {path}") from exc
        return cls({r["name"].lower(): Office(r["name"], r["room"], r["hours"]) for r in rows})

    @property
    def names(self) -> set[str]:
        return set(self._offices)

    def find(self, text: str) -> Office | None:
        t = text.lower()
        return next((o for name, o in self._offices.items() if name in t), None)


class Handbook:
    def __init__(self, rules: list[Rule]):
        self._rules = rules

    @classmethod
    def from_json(cls, path: Path) -> Handbook:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            raise DataError(f"handbook unreadable: {path}") from exc
        return cls([Rule(r["id"], r["title"], r["text"]) for r in raw])

    def search(self, query: str, min_score: int = 1) -> Rule | None:
        """Keyword overlap search (a baseline — retrieval improves in Week 3)."""
        words = {w for w in re.findall(r"\w+", query.lower()) if len(w) > 3}
        best, best_score = None, 0
        for rule in self._rules:
            score = sum(1 for w in words if w in rule.text.lower())
            if score > best_score:
                best, best_score = rule, score
        return best if best_score >= min_score else None
