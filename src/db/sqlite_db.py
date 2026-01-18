import sqlite3
from typing import List, Tuple, Dict, Set

class SQLiteDB:
    def __init__(self, path: str):
        self.path = path

    def tables(self) -> Dict[str, Set[str]]:
        with sqlite3.connect(self.path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = [r[0] for r in cur.fetchall()]
            out: Dict[str, Set[str]] = {}
            for t in tables:
                cur.execute(f"PRAGMA table_info({t});")
                cols = cur.fetchall()
                out[t] = {c[1] for c in cols}
        return out

    def execute(self, sql: str) -> List[Tuple]:
        with sqlite3.connect(self.path) as conn:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
        return rows

    def explain(self, sql: str) -> List[Tuple]:
        with sqlite3.connect(self.path) as conn:
            cur = conn.cursor()
            cur.execute(f"EXPLAIN {sql}")
            return cur.fetchall()

    def describe_schema(self) -> str:
        tbls = self.tables()
        lines = []
        for t, cols in tbls.items():
            col_defs = ", ".join(sorted(cols))
            lines.append(f"TABLE {t}({col_defs})")
        return "\n".join(lines)
