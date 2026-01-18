import os
from typing import Any, List, Tuple
from .base import Provider
from src.chain.prompting import build_sql_prompt

try:
    import ollama  # type: ignore
except Exception:
    ollama = None

SYSTEM_PROMPT = "You are a SQL assistant. Write SQLite queries using only the provided schema."

class OllamaProvider(Provider):
    name = "ollama"

    def __init__(self):
        if ollama is None:
            raise RuntimeError("ollama package not available")
        self.model = os.environ.get("OLLAMA_MODEL", "qwen3:1.7b")
        self.host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        # uses default ollama client

    def generate_sql(self, question, schema_context, few_shots=None):
        # minimal prompt for speed
        prompt = build_sql_prompt(schema_context, question, extra_examples=None)
        try:
            resp = ollama.chat(
                model=self.model, 
                messages=[{"role": "user", "content": prompt}], 
                stream=False, 
                options={"temperature": 0, "num_predict": 100}
            )
            return resp.get('message', {}).get('content', '').strip()
        except Exception as e:
            raise RuntimeError(f"ollama timeout or error: {e}")

    def summarize(self, question, rows):
        return f"Found {len(rows)} results for: {question}"
