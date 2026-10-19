import pytest
from pydantic import ValidationError
from assistant_core.models import Intent, Message, Source, Response


def test_message_valid():
    msg = Message(text="Xin chào")
    assert msg.text == "Xin chào"
    assert msg.session_id == "local"  


def test_message_empty_text_raises_validation_error():
    with pytest.raises(ValidationError) as exc_info:
        Message(text="")

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["type"] == "string_too_short"


def test_response_defaults():
    res = Response(answer="Xin chào bạn!", intent=Intent.GREETING)
    assert res.answer == "Xin chào bạn!"
    assert res.intent == Intent.GREETING
    assert res.sources == []  
    assert res.degraded is False  


def test_response_with_sources():
    source = Source(id="1", title="Hướng dẫn sử dụng")
    res = Response(
        answer="Chi tiết xem tại nguồn.",
        intent=Intent.RULE,
        sources=[source],
        degraded=True,
    )
    assert len(res.sources) == 1
    assert res.sources[0].id == "1"
    assert res.sources[0].title == "Hướng dẫn sử dụng"
    assert res.degraded is True