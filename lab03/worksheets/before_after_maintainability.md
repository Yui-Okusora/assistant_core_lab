# Lab 3 — Before / after maintainability comparison

Fill in for the monolith (before) and your refactored package (after).

| Question | Before | After |
|---|---|---|
| Where would you change the credit rate? How many places? | 1 constant in code | 1 variable in .env |
| Can you run the tests without internet or an API key? | no | yes |
| What happens if `handbook.json` is missing? | prints and continues silently | DataError at startup |
| Is any secret printed or logged? | yes | no |
| How long does it take a new teammate to find the fee logic? | days | minutes |
| Number of global variables | 9 (3 mutable) | 0 |
| Number of bare `except:` blocks | 3 | 0 |
| Lines in the longest function | ~65 (handle) | ~15 |
| `ruff check` issues | yes | no |
| Can you swap the LLM without touching the service? | no | yes |

**Three sentences:** what improved most, what got more complex, and what you would still change.
