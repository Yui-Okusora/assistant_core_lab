"""Create school.db from school.sql.   Run:  python make_school_db.py"""
import sqlite3
from pathlib import Path

here = Path(__file__).parent
con = sqlite3.connect(here / "school.db")
con.executescript((here / "school.sql").read_text(encoding="utf-8"))
con.commit()
for table in ("students", "courses", "enrollments"):
    n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"{table:12} {n} rows")
con.close()
