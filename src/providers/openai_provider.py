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
            raise RuntimeError("openai package not available")
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        self.client = OpenAI(api_key=api_key)
        self.model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    def generate_sql(self, question, schema_context):
        # skip dynamic examples to save tokens
        prompt = build_sql_prompt(schema_context, question)
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],  # no system prompt
                temperature=0,
                max_tokens=100,
                timeout=30,
            )
            content = resp.choices[0].message.content.strip()
            if not content:
                raise RuntimeError("OpenAI returned empty content")
            return content
        except Exception as e:
            if "quota" in str(e).lower() or "rate_limit" in str(e).lower():
                raise RuntimeError("OpenAI quota exceeded. Switch to --provider naive or ollama")
            raise

    def summarize(self, question, rows):
        return f"Found {len(rows)} results for: {question}"
