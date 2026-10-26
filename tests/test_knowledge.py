from fastapi.testclient import TestClient

from src.assistant_core.__main__ import create_app
from src.assistant_core.knowledge import Office, OfficeDirectory


def test_office_directory_all_returns_offices_sorted_by_name():
    training = Office("Training Office", "I.101", "Mon-Fri 07:30-16:30")
    library = Office("Library", "B.201", "Mon-Sat 07:00-20:00")
    directory = OfficeDirectory({"training office": training, "library": library})

    assert directory.all() == [library, training]


def test_get_offices_returns_sorted_records(service):
    response = TestClient(create_app(service)).get("/v1/offices")

    assert response.status_code == 200
    assert response.json() == [
        {"name": "IT Helpdesk", "room": "E.005", "hours": "Mon-Fri 08:00-17:00"},
        {"name": "Library", "room": "B.201", "hours": "Mon-Sat 07:00-20:00"},
        {"name": "Student Affairs", "room": "I.102", "hours": "Mon-Fri 08:00-16:00"},
        {"name": "Training Office", "room": "I.101", "hours": "Mon-Fri 07:30-16:30"},
    ]
