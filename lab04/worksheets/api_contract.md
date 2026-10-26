# Lab 4 — API contract worksheet

Fill in one row per endpoint **before** you code it.

| Method | Path | Request body / params | Success (code + body) | Errors (code + error.code) | Who calls it |
|---|---|---|---|---|---|
| GET | /health | — | 200 {status, version} | — | ops, UI |
| POST | /v1/chat | | | | UI, tests |
| POST | /v1/feedback | | | | UI |
| GET | /v1/feedback | header X-API-Key | | | staff dashboard |
| GET | /v1/weather | — | | | UI |

Questions:
1. Which fields are required, and what are their limits?
2. What does the UI show for each error code?
3. What changes would force a `/v2`?
