import pytest
from src.assistant_core.config import load_settings
from src.assistant_core.knowledge import Handbook, OfficeDirectory
from src.assistant_core.responder import StubLLMResponder
from src.assistant_core.service import AssistantService

@pytest.fixture
def service():
    settings = load_settings()
    offices = OfficeDirectory.from_csv(settings.data_dir / "offices.csv")
    handbook = Handbook.from_json(settings.data_dir / "handbook.json")
    responder = StubLLMResponder()
    return AssistantService(settings, offices, handbook, responder)