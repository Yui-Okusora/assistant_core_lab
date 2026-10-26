# Lab 4 homework — design for an external service that goes down

Service chosen (weather / maps / news / other approved): ____________  Base URL: ____________

| Failure | How you simulate it | What your API returns | What the user sees |
|---|---|---|---|
| timeout | transport raises ConnectTimeout | | |
| 500 from upstream | MockTransport returns 500 | | |
| malformed JSON | MockTransport returns `{}` | | |
| rate limited (429) | MockTransport returns 429 | | |

Timeout value and why: ____  Retries and why: ____  Cache TTL and why: ____
Tests added (file + names):
