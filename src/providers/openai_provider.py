import os
from typing import Any, List, Tuple
from .base import Provider
from src.chain.prompting import build_sql_prompt

try:
    from openai import OpenAI  # type: ignore
except Exception:
    OpenAI = None

SYSTEM_PROMPT = "You are a SQL assistant. Write SQLite queries using only the provided schema."

class OpenAIProvider(Provider):
    name = "openai"

    def __init__(self):
        if OpenAI is None:
            raise RuntimeError("openai package not available")
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        self.client = OpenAI(api_key=api_key)
        self.model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    def generate_sql(self, question, schema_context, few_shots=None):
        # skip dynamic examples to save tokens
        prompt = build_sql_prompt(schema_context, question, extra_examples=None)
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],  # no system prompt
                temperature=0,
                max_tokens=100
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            if "quota" in str(e).lower() or "rate_limit" in str(e).lower():
                raise RuntimeError("OpenAI quota exceeded. Switch to --provider naive or ollama")
            raise

    def summarize(self, question, rows):
        return f"Found {len(rows)} results for: {question}"
