"""Check your SQL answers.   Run:  python check.py   (optionally: python check.py my_answers.sql)

For each question it runs your query on school.db and compares the result with expected.json.
"""
import json
import re
import sqlite3
import sys
from pathlib import Path

here = Path(__file__).parent
db = here / "school.db"
if not db.exists():
    sys.exit("school.db not found — run:  python make_school_db.py")


def split(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    parts = re.split(r"^--\s*(Q\d+)\b.*$", text, flags=re.M)
    out = {}
    for i in range(1, len(parts), 2):
        body = "\n".join(line for line in parts[i + 1].splitlines() if not line.strip().startswith("--")).strip()
        out[parts[i]] = body
    return out


mine = split(Path(sys.argv[1]) if len(sys.argv) > 1 else here / "my_answers.sql")
ref = json.loads((here / "expected.json").read_text(encoding="utf-8"))
con = sqlite3.connect(db)
score = 0
for q in sorted(ref, key=lambda k: int(k[1:])):
    sql = mine.get(q, "")
    if not sql:
        print(f"{q:4} ..  not answered yet")
        continue
    try:
        got = con.execute(sql).fetchall()
    except sqlite3.Error as exc:
        print(f"{q:4} ERR {exc}")
        continue
    got = [list(r) for r in got]
    want, ordered = ref[q]["rows"], ref[q]["ordered"]
    same = got == want if ordered else sorted(map(repr, got)) == sorted(map(repr, want))
    score += same
    print(f"{q:4} {'OK ' if same else 'NO '} " + ("" if same else f"expected {want[:3]}{' ...' if len(want) > 3 else ''}, got {got[:3]}"))
print(f"\nScore: {score}/{len(ref)}")
