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


# def test_<your_bug_1>(...):
# def test_<your_bug_2>(...):
# def test_<your_bug_3>(...):
