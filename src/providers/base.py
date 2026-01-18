from typing import Any, List, Tuple, Optional, Dict

class Provider:
    name = "base"

    def generate_sql(self, question, schema_context, few_shots=None):
        raise NotImplementedError

    def summarize(self, question, rows):
        return f"Found {len(rows)} results"
