from pathlib import Path

import pytest

from assistant_core.config import Settings
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.responder import StubLLMResponder
from assistant_core.service import AssistantService

DATA = Path(__file__).resolve().parents[1] / "data"


@pytest.fixture
def settings():
    return Settings(data_dir=DATA)


@pytest.fixture
def service(settings):
    return AssistantService(
        settings,
        OfficeDirectory.from_csv(DATA / "offices.csv"),
        Handbook.from_json(DATA / "handbook.json"),
        StubLLMResponder(),
    )
