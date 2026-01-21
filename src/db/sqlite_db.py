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
        with sqlite3.connect(self.path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = [r[0] for r in cur.fetchall()]
            lines = []
            for t in tables:
                cur.execute(f"PRAGMA table_info({t});")
                cols = cur.fetchall()
                col_lines = []
                for c in cols:
                    col_name = c[1]
                    col_type = c[2]
                    pk = ' PRIMARY KEY' if c[5] else ''
                    col_lines.append(f"  {col_name} {col_type}{pk}")
                # foreign keys
                cur.execute(f"PRAGMA foreign_key_list({t});")
                fks = cur.fetchall()
                fk_lines = [f"  FOREIGN KEY ({fk[3]}) REFERENCES {fk[2]}({fk[4]})" for fk in fks]
                lines.append(f"TABLE {t} (\n" + ",\n".join(col_lines + fk_lines) + "\n)")
                # add sample row
                try:
                    cur.execute(f"SELECT * FROM {t} LIMIT 1;")
                    row = cur.fetchone()
                    if row:
                        example = ', '.join(f"{col[1]}={repr(val)}" for col, val in zip(cols, row))
                        lines.append(f"  -- Example: {example}")
                except Exception:
                    pass
            return "\n".join(lines)
 