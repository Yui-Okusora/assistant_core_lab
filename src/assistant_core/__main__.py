import logging
import sys
import time

from pydantic import ValidationError

from assistant_core.config import load_settings
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.logging_setup import setup_logging
from assistant_core.models import Message
from assistant_core.responder import StubLLMResponder
from assistant_core.service import AssistantService

log = logging.getLogger("assistant_core")


def main():
    settings = load_settings()
    setup_logging(settings.log_level)

    offices = OfficeDirectory.from_csv(settings.data_dir / "offices.csv")
    handbook = Handbook.from_json(settings.data_dir / "handbook.json")
    responder = StubLLMResponder()
    service = AssistantService(settings, offices, handbook, responder)
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "hi"

    start = time.perf_counter()

    try:
        msg = Message(text=query)
        res = service.handle(msg)
        latency_ms = round((time.perf_counter() - start) * 1000, 1)
        log.info(
            "handled",
            extra={
                "intent": res.intent.value,
                "latency_ms": latency_ms,
                "session": msg.session_id,
                "degraded": res.degraded,
            },
        )

        print(res.answer)

    except ValidationError:
        print("Error: Message cannot be empty.")


if __name__ == "__main__":
    main()
