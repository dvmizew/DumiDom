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
            raise RuntimeError("OpenAI provider error: 'openai' package not installed. Please install openai>=1.0.0 in your environment.")
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OpenAI provider error: OPENAI_API_KEY environment variable not set. Set your API key to use this provider.")
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
                raise RuntimeError("OpenAI provider error: API returned empty content. Check your model and API key.")
            return content
        except Exception as e:
            msg = str(e)
            if "quota" in msg.lower() or "rate_limit" in msg.lower():
                raise RuntimeError(
                    "OpenAI provider error: Your OpenAI quota has been exceeded or you hit a rate limit. "
                    "Please check your OpenAI account usage and billing at https://platform.openai.com/account/usage. "
                    "You can switch to --provider naive or ollama to continue benchmarking."
                )
            if "401" in msg or "unauthorized" in msg.lower():
                raise RuntimeError("OpenAI provider error: Unauthorized. Check your OPENAI_API_KEY.")
            if "timeout" in msg.lower():
                raise RuntimeError("OpenAI provider error: Request timed out. Try again later.")
            raise RuntimeError(f"OpenAI provider error: {msg}")

    def summarize(self, question, rows):
        return f"Found {len(rows)} results for: {question}"
