import sqlite3
from typing import List, Tuple, Dict, Set
 
class SQLiteDB:
    def __init__(self, path: str):
        self.path = path
 
    def tables(self) -> Dict[str, Set[str]]:
        with sqlite3.connect(self.path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            out = {}
            for (t,) in cur.fetchall():
                cur.execute(f"PRAGMA table_info({t});")
                out[t] = {c[1] for c in cur.fetchall()}
        return out
 
    def execute(self, sql: str) -> List[Tuple]:
        with sqlite3.connect(self.path) as conn:
            cur = conn.cursor()
            cur.execute(sql)
            return cur.fetchall()
 
    def explain(self, sql: str) -> List[Tuple]:
        with sqlite3.connect(self.path) as conn:
            cur = conn.cursor()
            cur.execute(f"EXPLAIN {sql}")
            return cur.fetchall()
 
    def describe_schema(self) -> str:
        with sqlite3.connect(self.path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            lines = []
            for (t,) in cur.fetchall():
                cur.execute(f"PRAGMA table_info({t});")
                cols = cur.fetchall()
                col_lines = [f"  {c[1]} {c[2]}{' PRIMARY KEY' if c[5] else ''}" for c in cols]
                cur.execute(f"PRAGMA foreign_key_list({t});")
                fks = cur.fetchall()
                fk_lines = [f"  FOREIGN KEY ({fk[3]}) REFERENCES {fk[2]}({fk[4]})" for fk in fks]
                lines.append(f"TABLE {t} (\n" + ",\n".join(col_lines + fk_lines) + "\n)")
                try:
                    cur.execute(f"SELECT * FROM {t} LIMIT 1;")
                    row = cur.fetchone()
                    if row:
                        example = ', '.join(f"{c[1]}={repr(val)}" for c, val in zip(cols, row))
                        lines.append(f"  -- Example: {example}")
                except Exception:
                    continue
            return "\n".join(lines)
 