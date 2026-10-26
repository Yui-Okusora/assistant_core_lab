"""Run: pytest -q test_hello_api.py   — all green means P1–P5 are done."""
from fastapi.testclient import TestClient

from hello_api import app

client = TestClient(app)


def test_p1_home():
    assert client.get("/").json() == {"message": "Hello, CSC10014!"}


def test_p2_hello():
    assert client.get("/hello/Lan").json() == {"message": "Hello, Lan!"}


def test_p3_square():
    assert client.get("/square?n=7").json() == {"n": 7, "square": 49}
    assert client.get("/square?n=abc").status_code == 422      # FastAPI checks the type for you


def test_p4_add():
    r = client.post("/add", json={"a": 2, "b": 3})
    assert r.status_code == 200 and r.json() == {"sum": 5}


def test_p5_course():
    assert client.get("/courses/CSC10014").json()["name"] == "Computational Thinking"
    assert client.get("/courses/XYZ").status_code == 404
