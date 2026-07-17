# webhook.py
import os
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from agent import resume_rca

load_dotenv()

app = FastAPI()

# Almacén temporal de threads pendientes de aprobación
# En producción esto sería una base de datos
pending_threads: dict[str, bool] = {}


@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    """
    Recibe updates de Telegram.
    El operador responde con /aprobar <thread_id> o /rechazar <thread_id>
    """
    data = await request.json()

    message = data.get("message", {})
    text = message.get("text", "")

    if text.startswith("/aprobar"):
        parts = text.split()
        if len(parts) < 2:
            return {"ok": True}
        thread_id = parts[1]
        print(f"Aprobación recibida para thread: {thread_id}")
        result = resume_rca(thread_id=thread_id, approved=True)
        last_msg = result["messages"][-1].content
        print(f"Agente reanudado. Resultado: {last_msg[:200]}")

    elif text.startswith("/rechazar"):
        parts = text.split()
        if len(parts) < 2:
            return {"ok": True}
        thread_id = parts[1]
        print(f"Rechazo recibido para thread: {thread_id}")
        result = resume_rca(thread_id=thread_id, approved=False)
        last_msg = result["messages"][-1].content
        print(f"Agente reanudado. Resultado: {last_msg[:200]}")

    return {"ok": True}


@app.get("/health")
def health():
    return {"status": "ok"}