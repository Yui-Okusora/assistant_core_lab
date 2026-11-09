"""AssistantService: the single entry point used by the CLI, the API (Lab 4) and the UI (Lab 7)."""

from __future__ import annotations

import logging
import time

from assistant_core.config import Settings
from assistant_core.errors import InvalidRequest, ProviderError
from assistant_core.guard import PRIVATE_REPLY, is_private_request
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.llm import make_llm
from assistant_core.models import Intent, Message, Response, Source
from assistant_core.rag.answerer import RagAnswerer
from assistant_core.rag.chunker import load_folder
from assistant_core.rag.index import make_index
from assistant_core.responder import Responder, TemplateResponder, make_responder
from assistant_core.router import route
from assistant_core.tools import parse_credits, run_tool_call, tuition

log = logging.getLogger("assistant_core")


class AssistantService:
    def __init__(
        self,
        settings: Settings,
        offices: OfficeDirectory,
        handbook: Handbook,
        responder: Responder,
        rag: RagAnswerer | None = None,
    ):
        self.settings = settings
        self.offices = offices
        self.handbook = handbook
        self.responder = responder
        self.fallback = TemplateResponder()
        self.rag = rag

    def handle(self, msg: Message) -> Response:
        start = time.perf_counter()
        intent = route(msg.text, self.offices.names)
        resp = self._dispatch(intent, msg.text)
        log.info(
            "handled",
            extra={
                "intent": resp.intent.value,
                "degraded": resp.degraded,
                "session": msg.session_id,
                "latency_ms": round((time.perf_counter() - start) * 1000, 1),
            },
        )
        return resp

    def _dispatch(self, intent: Intent, text: str) -> Response:
        if intent is Intent.GREETING:
            return Response(answer="Hello! I can help with offices, fees and rules.", intent=intent)
        if intent is Intent.FEE:
            return self._fee(text)
        if intent is Intent.OFFICE:
            o = self.offices.find(text)
            return Response(answer=f"{o.name}: room {o.room}, open {o.hours}.", intent=intent)
        return self._rule(text)

    def _fee(self, text: str) -> Response:
        s = self.settings
        try:
            credits, retake = parse_credits(text)
            total = tuition(credits, retake, s.credit_rate_vnd, s.retake_multiplier, s.max_credits)
        except InvalidRequest as exc:
            return Response(answer=str(exc), intent=Intent.FEE)
        return Response(answer=f"Your tuition is {total:,} VND.", intent=Intent.FEE)

    def _rule(self, text: str) -> Response:
        if self.rag is not None:  # Lab 6: guard, then retrieval + LLM with abstain
            if is_private_request(text):
                return Response(answer=PRIVATE_REPLY, intent=Intent.UNKNOWN, path="abstain", escalate=False)
            return self.rag.answer(text)
        rule = self.handbook.search(text)
        if rule is None:
            return Response(answer="Sorry, I don't know that yet.", intent=Intent.UNKNOWN)
        sources = [Source(id=rule.id, title=rule.title)]
        try:
            return Response(answer=self.responder.explain(text, rule), intent=Intent.RULE, sources=sources)
        except ProviderError:
            log.warning("provider failed; using template fallback")
            answer = self.fallback.explain(text, rule)
            return Response(answer=answer, intent=Intent.RULE, sources=sources, degraded=True)


def build_service(settings: Settings) -> AssistantService:
    d = settings.data_dir
    offices = OfficeDirectory.from_csv(d / "offices.csv")
    handbook = Handbook.from_json(d / "handbook.json")
    responder_name = settings.llm_provider if settings.llm_provider in ("stub", "template") else "template"
    rag = None
    if settings.kb_dir.exists():
        index = make_index(settings.retrieval_kind, load_folder(settings.kb_dir))
        llm = (
            None
            if settings.llm_provider == "template"
            else make_llm(
                settings.llm_provider,
                settings.llm_model,
                settings.llm_base_url,
                settings.llm_api_key,
                settings.llm_timeout_s,
            )
        )

        def tool_runner(raw: str) -> str | None:
            return run_tool_call(raw, settings.credit_rate_vnd, settings.retake_multiplier, settings.max_credits)

        rag = RagAnswerer(
            index, llm, settings.retrieval_min_score, prompt_version=settings.prompt_version, tool_runner=tool_runner
        )
    return AssistantService(settings, offices, handbook, make_responder(responder_name), rag)
