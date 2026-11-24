"""Lab 8 Part E: turn YOUR Week-7 failures into regression tests.

Write at least three tests. Each one must:
  - have a name that says what went wrong, e.g. test_empty_sources_does_not_crash_ui
  - FAIL on the old code (check by temporarily undoing your fix), and PASS after the fix.
Use the fixtures `service`, `settings` from conftest.py, or build a TestClient like tests/test_security.py.
"""
from assistant_core.models import Message


def test_example_greeting_still_works(service):
    """Example: a control case that must never break."""
    assert "Hello" in service.handle(Message(text="hi")).answer


def test_retake_number_as_word(service):
    """BUG-7: 'two retakes' was ignored and the total was too low."""
    r = service.handle(Message(text="tuition for 18 credits and two retakes"))
    assert "8,100,000" not in r.answer  
    assert "digits" in r.answer.lower()


def test_fee_out_of_range_credits_gives_no_amount(service):
    """BUG-8: Out-of-range credit counts (e.g., 99 credits) still returned a fee amount."""
    r = service.handle(Message(text="tuition for 99 credits"))
    assert "VND" not in r.answer


def test_whitespace_only_message_handled_gracefully(service):
    """BUG-9: Whitespace-only input caused an unhandled error or empty response."""
    r = service.handle(Message(text="     "))
    assert r.answer.strip() != ""