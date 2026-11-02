#!/usr/bin/env python3
"""Fill the database with SYNTHETIC interactions and feedback (no real data).

python scripts/seed.py assistant.db 300
"""

import random
import sys
import uuid

from assistant_api.db import Repository, init_db, make_engine

db_path = sys.argv[1] if len(sys.argv) > 1 else "assistant.db"
n = int(sys.argv[2]) if len(sys.argv) > 2 else 300
random.seed(7)
engine = make_engine(f"sqlite:///{db_path}")
init_db(engine)
repo = Repository(engine, "seed-salt")

PLAN = [
    ("greeting", None, 0.99, 2),
    ("fee", None, 0.95, 5),
    ("office", None, 0.97, 3),
    ("rule", "H26-5.3", 0.85, 40),
    ("rule", "H26-4.2", 0.80, 45),
    ("rule", "H26-7.2", 0.70, 60),
    ("unknown", None, 0.0, 8),
]
WEIGHTS = [10, 20, 15, 25, 15, 5, 10]
for _ in range(n):
    intent, topic, ok_rate, base_ms = random.choices(PLAN, WEIGHTS)[0]
    rid = uuid.uuid4().hex[:12]
    resolved = intent != "unknown"
    degraded = resolved and random.random() > ok_rate
    repo.record_interaction(
        f"student-{random.randint(1, 60)}",
        rid,
        intent,
        topic,
        resolved,
        degraded,
        round(random.gauss(base_ms * (4 if degraded else 1), base_ms / 3), 1),
    )
    if random.random() < 0.3:
        good = resolved and not degraded
        repo.add_feedback(rid, 1 if good and random.random() < 0.85 else -1, None)
print(f"seeded {n} interactions into {db_path}")
