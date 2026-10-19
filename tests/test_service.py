from src.assistant_core.models import Message
from src.assistant_core.responder import StubLLMResponder

def test_fallback_when_provider_fails(service):
    service.responder = StubLLMResponder(fail=True)
    r = service.handle(Message(text="thesis registration credits"))
    assert r.degraded and r.sources
