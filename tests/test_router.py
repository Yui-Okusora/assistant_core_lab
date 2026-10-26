from assistant_core.models import Intent
from assistant_core.router import route

OFFICES = {"library", "training office"}


def test_greeting():
    assert route("Hello!", OFFICES) is Intent.GREETING


def test_fee():
    assert route("tuition for 18 credits", OFFICES) is Intent.FEE


def test_office():
    assert route("where is the library", OFFICES) is Intent.OFFICE


def test_default_rule():
    assert route("can I register my thesis", OFFICES) is Intent.RULE
