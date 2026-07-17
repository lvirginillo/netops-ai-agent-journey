# telegram_bot.py
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_API = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}"
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_message(text: str) -> bool:
    try:
        response = httpx.post(
            f"{TELEGRAM_API}/sendMessage",
            json={"chat_id": CHAT_ID, "text": text},  # sin parse_mode
            timeout=10,
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Error enviando mensaje Telegram: {e}")
        return False


def send_approval_request(thread_id: str, action: str, detail: str) -> bool:
    message = (
        f"Aprobacion requerida\n\n"
        f"Incidente: {thread_id}\n"
        f"Accion propuesta: {action}\n"
        f"Detalle: {detail}\n\n"
        f"Responde con:\n"
        f"/aprobar {thread_id}\n"
        f"/rechazar {thread_id}"
    )
    return send_message(message)