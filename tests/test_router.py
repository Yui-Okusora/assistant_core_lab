from src.assistant_core.router import route, Intent

def test_greeting_intent():
    assert route("hello", set()) == Intent.GREETING
    assert route("xin chao!", set()) == Intent.GREETING

def test_fee_intent():
    assert route("what is the tuition?", set()) == Intent.FEE
    assert route("fee info", set()) == Intent.FEE

def test_office_intent():
    offices = {"registrar", "admissions"}
    assert route("where is admissions?", offices) == Intent.OFFICE

def test_rule_intent():
    assert route("tell me about the rules", set()) == Intent.RULE