import os
import httpx
from typing import Optional

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
_BASE = "https://api.telegram.org/bot"


def send_telegram_message(chat_id: str, text: str) -> tuple[bool, Optional[str]]:
    if not TELEGRAM_BOT_TOKEN:
        return False, "TELEGRAM_BOT_TOKEN nao configurado."
    try:
        resp = httpx.post(
            f"{_BASE}{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
        resp.raise_for_status()
        return True, None
    except httpx.HTTPStatusError as e:
        return False, f"Telegram HTTP {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return False, str(e)
