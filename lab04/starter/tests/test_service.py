import pytest
from pydantic import ValidationError

from assistant_core.models import Intent, Message
from assistant_core.responder import StubLLMResponder


def test_fee_answer(service):
    r = service.handle(Message(text="tuition for 18 credits and 2 retake"))
    assert r.intent is Intent.FEE and "9,450,000" in r.answer


def test_rule_has_source(service):
    r = service.handle(Message(text="can I register my thesis with 118 credits"))
    assert r.intent is Intent.RULE and r.sources[0].id == "H26-5.3"


def test_fallback_when_provider_fails(service):
    service.responder = StubLLMResponder(fail=True)
    r = service.handle(Message(text="thesis registration credits"))
    assert r.degraded and r.sources


def test_unknown(service):
    assert service.handle(Message(text="what is the weather")).intent is Intent.UNKNOWN


def test_empty_message_rejected():
    with pytest.raises(ValidationError):
        Message(text="")
