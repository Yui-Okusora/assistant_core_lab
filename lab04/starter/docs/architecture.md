# assistant_core — architecture note (reference solution)

## Modules and responsibilities
| Module | Responsibility | Depends on |
|---|---|---|
| `config.py` | read settings from env / `.env`; validate | errors |
| `models.py` | public contract: `Message`, `Response`, `Intent`, `Source` | pydantic |
| `router.py` | choose an `Intent` with rules | models |
| `knowledge.py` | `OfficeDirectory` (CSV), `Handbook` (JSON) + keyword search | errors |
| `tools.py` | deterministic tuition calculation | errors |
| `responder.py` | `Responder` interface; template + stub LLM | knowledge, errors |
| `service.py` | `AssistantService.handle(Message) -> Response`; fallback | all of the above |
| `logging_setup.py` | JSON logs, no secrets | — |
| `__main__.py` | CLI entry point | service, config |

## Service interface
```
AssistantService.handle(msg: Message) -> Response
```
Input: `Message(text: 1–2000 chars, session_id)`. Output: `Response(answer, intent, sources, degraded)`.
Errors: invalid input raises `pydantic.ValidationError`; startup problems raise `ConfigError` / `DataError`;
provider failures never reach the caller — the service falls back to the template responder and sets `degraded=True`.

## Decisions
- Fees are computed in `tools.py`, never by an LLM (exact, testable).
- The LLM is behind `Responder`; `stub` needs no key, so tests and CI run offline.
- Configuration comes from the environment (Twelve-Factor III); `.env.example` documents every variable.
