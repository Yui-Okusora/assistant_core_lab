#!/usr/bin/env python3
"""Compare three assistant paths on eval/cases.jsonl.

deterministic — router + tools only; rule questions are not answered
retrieval     — router + tools + retrieval, quoting the best source (no LLM)
llm           — router + tools + retrieval + LLM with structured output (provider from .env; stub by default)

  python eval/compare_paths.py
"""

from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

from assistant_core.config import load_settings
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.llm import make_llm
from assistant_core.models import Message
from assistant_core.rag.answerer import RagAnswerer
from assistant_core.rag.chunker import load_folder
from assistant_core.rag.index import make_index
from assistant_core.responder import TemplateResponder
from assistant_core.service import AssistantService


class NoAnswer:
    """Deterministic path: never answers from documents."""

    def search(self, query, k=3):
        return []


def correct(case: dict, resp) -> bool:
    if case.get("expect_abstain"):
        return resp.path == "abstain" or resp.intent.value == "unknown"
    if "expect_contains" in case:
        return case["expect_contains"] in resp.answer
    return any(s.id == case["expect_source"] for s in resp.sources)


def main() -> int:
    s = load_settings()
    cases = [json.loads(line) for line in Path("eval/cases.jsonl").read_text(encoding="utf-8").splitlines() if line]
    offices = OfficeDirectory.from_csv(s.data_dir / "offices.csv")
    handbook = Handbook.from_json(s.data_dir / "handbook.json")
    chunks = load_folder(s.kb_dir)
    index = make_index(s.retrieval_kind, chunks)
    provider = s.llm_provider if s.llm_provider != "template" else "stub"
    llm = make_llm(provider, s.llm_model, s.llm_base_url, s.llm_api_key, s.llm_timeout_s)
    paths = {
        "deterministic": RagAnswerer(NoAnswer(), None, s.retrieval_min_score),
        "retrieval": RagAnswerer(index, None, s.retrieval_min_score),
        f"llm ({llm.name})": RagAnswerer(index, llm, s.retrieval_min_score, prompt_version=s.prompt_version),
    }
    print(f"{'path':18} {'correct':>8} {'abstain ok':>11} {'p50 ms':>7} {'max ms':>7}")
    for name, rag in paths.items():
        svc = AssistantService(s, offices, handbook, TemplateResponder(), rag)
        ok = abst_ok = abst_total = 0
        lat, fails = [], []
        for c in cases:
            t0 = time.perf_counter()
            r = svc.handle(Message(text=c["question"]))
            lat.append((time.perf_counter() - t0) * 1000)
            good = correct(c, r)
            ok += good
            if c.get("expect_abstain"):
                abst_total += 1
                abst_ok += good
            if not good:
                fails.append(c["id"])
        print(
            f"{name:18} {ok:>5}/{len(cases)} {abst_ok:>7}/{abst_total} {statistics.median(lat):7.1f} {max(lat):7.1f}"
            f"   fails: {' '.join(fails)}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
