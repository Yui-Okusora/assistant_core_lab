"""assistant_core — the service layer of the CSC10014 study assistant."""

from assistant_core.models import Message, Response
from assistant_core.service import AssistantService, build_service

__all__ = ["AssistantService", "Message", "Response", "build_service"]
