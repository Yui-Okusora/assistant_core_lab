import pytest

from src.assistant_core.tools import InvalidRequest, parse_credits, tuition


def test_parse_with_retake():
    assert parse_credits("tuition for 18 credits and 2 retake") == (18, 2)
    
def test_tuition_value():
    assert tuition(18, 2, 450_000, 1.5, 30) == 9_450_000 # same as the monolith
    
@pytest.mark.parametrize("credits", [0, 31])
def test_tuition_out_of_range(credits):
    with pytest.raises(InvalidRequest):
        tuition(credits, 0, 450_000, 1.5, 30)