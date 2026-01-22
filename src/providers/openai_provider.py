import os
from .base import Provider
from src.chain.text_to_sql import build_sql_prompt

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

class OpenAIProvider(Provider):
    name = "openai"

    def __init__(self):
        if OpenAI is None:
            raise RuntimeError("OpenAI provider: 'openai' package not installed.")
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OpenAI provider: OPENAI_API_KEY not set.")
        self.client = OpenAI(api_key=api_key)
        self.model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    def generate_sql(self, question, schema_context):
        prompt = build_sql_prompt(schema_context, question)
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=100,
                timeout=30,
            )
            content = resp.choices[0].message.content.strip()
            if not content:
                raise RuntimeError("OpenAI provider: API returned empty content.")
            return content
        except Exception as e:
            msg = str(e).lower()
            if any(x in msg for x in ["quota", "rate_limit"]):
                raise RuntimeError("OpenAI provider: quota/rate limit error.")
            if "401" in msg or "unauthorized" in msg:
                raise RuntimeError("OpenAI provider: unauthorized.")
            if "timeout" in msg:
                raise RuntimeError("OpenAI provider: timeout.")
            raise RuntimeError(f"OpenAI provider: {msg}")

    def summarize(self, question, rows):
        return f"Found {len(rows)} results for: {question}"
