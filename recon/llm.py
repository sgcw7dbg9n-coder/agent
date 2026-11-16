import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_PROVIDERS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "key_var": "GROQ_API_KEY",
        "model_var": "GROQ_MODEL",
        "default_model": "openai/gpt-oss-120b",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "key_var": "DEEPSEEK_API_KEY",
        "model_var": "DEEPSEEK_MODEL",
        "default_model": "deepseek-chat",
    },
}


def get_llm():
    provider = os.getenv("PROVIDER", "groq")
    if provider not in _PROVIDERS:
        raise SystemExit(f"Unknown PROVIDER '{provider}'. Use one of: {', '.join(_PROVIDERS)}")

    cfg = _PROVIDERS[provider]
    api_key = os.getenv(cfg["key_var"])
    if not api_key:
        raise SystemExit(f"No API key found in {cfg['key_var']}. Check your .env file.")

    client = OpenAI(api_key=api_key, base_url=cfg["base_url"])
    model = os.getenv(cfg["model_var"], cfg["default_model"])
    return client, model