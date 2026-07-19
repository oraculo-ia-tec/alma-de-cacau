import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(
    dotenv_path=Path(__file__).resolve().parent / ".env",
    override=False,
)


def get_env(name: str, default: str | None = None, required: bool = False) -> str | None:
    value = os.getenv(name, default)

    if required and not value:
        raise RuntimeError(f"Variavel obrigatoria nao configurada: {name}")

    return value


ASAAS_API_KEY = get_env("ASAAS_API_KEY", required=True)
DATABASE_URL = get_env("DATABASE_URL", required=True)
APP_BASE_URL = get_env("APP_BASE_URL", "http://localhost:8501")

GROQ_API_KEY = get_env("GROQ_API_KEY", required=True)
GROQ_MODEL = get_env("GROQ_MODEL", "llama-3.3-70b-versatile")

EMAIL_HOST = get_env("EMAIL_HOST")
EMAIL_PORT = int(get_env("EMAIL_PORT", "587"))
EMAIL_USERNAME = get_env("EMAIL_USERNAME")
EMAIL_PASSWORD = get_env("EMAIL_PASSWORD")
EMAIL_USE_TLS = get_env("EMAIL_USE_TLS", "true").lower() == "true"
EMAIL_USE_SSL = get_env("EMAIL_USE_SSL", "false").lower() == "true"
EMAIL_REMETENTE = get_env("EMAIL_REMETENTE")

PIXVERSE_API_KEY = get_env("PIXVERSE_API_KEY")
ASAAS_ENV = get_env("ASAAS_ENV", "sandbox")
TELEGRAM_BOT_TOKEN = get_env("TELEGRAM_BOT_TOKEN")
