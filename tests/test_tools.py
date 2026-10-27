import pytest

from assistant_core.errors import InvalidRequest
from assistant_core.tools import parse_credits, tuition


def test_parse_with_retake():
    assert parse_credits("tuition for 18 credits and 2 retake") == (18, 2)


def test_parse_same_numbers():
    assert parse_credits("fee 2 credits 2 retake") == (2, 2)


def test_parse_missing():
    with pytest.raises(InvalidRequest):
        parse_credits("how much is the fee?")


def test_tuition_value():
    assert tuition(18, 2, 450_000, 1.5, 30) == 9_450_000


@pytest.mark.parametrize("credits", [0, 31])
def test_tuition_out_of_range(credits):
    with pytest.raises(InvalidRequest):
        tuition(credits, 0, 450_000, 1.5, 30)
