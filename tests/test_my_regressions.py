import ast
from pathlib import Path

from assistant_core.models import Message

UI_APP_PATH = Path(__file__).resolve().parents[1] / "ui" / "app.py"


def test_example_greeting_still_works(service):
    """Control case: basic greeting must never break."""
    assert "Hello" in service.handle(Message(text="hi")).answer


def test_bug1_retake_number_as_word(service):
    """BUG-1: 'tuition for 18 credits and two retakes' must include the 2 retakes (9,450,000 VND)."""
    r = service.handle(Message(text="tuition for 18 credits and two retakes"))
    assert "8,100,000" not in r.answer
    assert "9,450,000" in r.answer


def test_bug2_feedback_buttons_trigger_rerun():
    """BUG-2: Clicking thumbs up/down in ui/app.py must call st.rerun() so buttons disappear immediately."""
    source = UI_APP_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    feedback_if_blocks = []
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            test_code = ast.unparse(node.test)
            if "button(" in test_code and ("👍" in test_code or "👎" in test_code):
                feedback_if_blocks.append(node)

    assert len(feedback_if_blocks) >= 2, "Expected both 👍 and 👎 button handlers in ui/app.py"

    for block in feedback_if_blocks:
        body_calls = [
            ast.unparse(sub.func)
            for sub in ast.walk(block)
            if isinstance(sub, ast.Call)
        ]
        assert any(call.endswith("rerun") for call in body_calls), (
            f"Missing st.rerun() inside feedback button handler: {ast.unparse(block.test)}"
        )


def test_bug3_sidebar_labels_are_english():
    """BUG-3: Sidebar buttons in ui/app.py must use English labels instead of Vietnamese."""
    ui_source = UI_APP_PATH.read_text(encoding="utf-8")
    assert "Xóa lịch sử trò chuyện" not in ui_source
    assert "Tải lịch sử chat" not in ui_source