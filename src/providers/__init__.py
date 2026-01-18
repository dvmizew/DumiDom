from .base import Provider
from .naive_provider import NaiveProvider
try:
    from .openai_provider import OpenAIProvider
except Exception:
    OpenAIProvider = None
try:
    from .ollama_provider import OllamaProvider
except Exception:
    OllamaProvider = None

PROVIDERS = {
    "naive": NaiveProvider,
    "openai": OpenAIProvider,
    "ollama": OllamaProvider,
}
