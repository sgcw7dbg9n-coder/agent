import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

provider = os.getenv("PROVIDER", "groq")

config = {
    "groq": {
        "api_key": os.getenv("GROQ_API_KEY"),
        "base_url": "https://api.groq.com/openai/v1",
        "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
    },
    "deepseek": {
        "api_key": os.getenv("DEEPSEEK_API_KEY"),
        "base_url": "https://api.deepseek.com",
        "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    },
}[provider]

if not config["api_key"]:
    raise SystemExit(f"No API key found for provider '{provider}'. Check your .env file.")

client = OpenAI(api_key=config["api_key"], base_url=config["base_url"])

response = client.chat.completions.create(
    model=config["model"],
    messages=[
        {"role": "user", "content": "Reply with one short sentence confirming you are working."}
    ],
)

print(f"Provider: {provider} | Model: {config['model']}")
print(response.choices[0].message.content)