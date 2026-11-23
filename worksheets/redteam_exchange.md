# Lab 8 — Red-team exchange

## Rules of engagement
- Attack only the partner team's assistant, running on **their laptop or staging** — never university systems.
- No real personal data. No flooding (max 1 request per second).
- Stop and tell the owners if you find something serious (e.g. a secret in a response).

## Steps
1. Write 8–10 attack cases for the partner team in `redteam/cases_for_<team>.jsonl` (same format as `redteam/cases.jsonl`).
   Cover: prompt injection, privacy, out-of-scope, malformed input, fee manipulation, unavailable service.
2. Send the file to the partner team (PR to their repo or chat).
3. The owners run: `python redteam/run_redteam.py redteam/cases_for_<team>.jsonl`
4. Together, go through every FAIL: agree on severity, write a bug report, add it to the failure catalogue.

## Results
| Case | Result | Severity | Bug report |
|---|---|---|---|
| | | | |
