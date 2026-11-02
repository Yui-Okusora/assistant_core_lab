import sqlite3
from pathlib import Path

import pytest

import school_repo as repo

SQL = (Path(__file__).parent / "school.sql").read_text(encoding="utf-8")


@pytest.fixture
def con():
    c = sqlite3.connect(":memory:")          # a fresh in-memory copy for every test
    c.executescript(SQL)
    yield c
    c.close()


def test_example_students_in_program(con):
    assert repo.students_in_program(con, "CS") == ["An", "Chi", "Hoa"]


def test_d1_add_student(con):
    new_id = repo.add_student(con, "Minh", 1, "CS")
    assert new_id == 9
    assert "Minh" in repo.students_in_program(con, "CS")


def test_d1_no_sql_injection(con):
    repo.add_student(con, "Robert'); DROP TABLE students;--", 1, "CS")
    assert con.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 9     # table still there


def test_d2_average_grade(con):
    assert repo.average_grade(con, "CSC10004") == 5.25
    assert repo.average_grade(con, "XYZ") is None


def test_d3_transcript(con):
    assert repo.transcript(con, 2) == [("Computational Thinking", 3, None), ("Data Structures and Algorithms", 4, 5.5),
                                       ("Fundamentals of Programming", 4, 7.0)]
