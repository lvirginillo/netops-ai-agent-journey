# resume.py
from agent import run_rca, resume_rca
from telegram_bot import send_approval_request

ALERT = """
Cliente: AS65005
Síntoma: El cliente reporta pérdida total de conectividad BGP.
Dispositivo afectado: dist-sw02 (10.10.20.178)
Hora del reporte: hace 5 minutos
"""

THREAD_ID = "incidente-001"

print("Iniciando agente...\n")
result = run_rca(alert=ALERT, thread_id=THREAD_ID)

last_msg = result["messages"][-1]
if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
    tool_name = last_msg.tool_calls[0]["name"]
    tool_args = last_msg.tool_calls[0]["args"]

    print(f"⏸  PAUSADO — acción pendiente: {tool_name}({tool_args})")
    print(f"   Thread ID: {THREAD_ID}\n")

    # Notificar al operador por Telegram
    send_approval_request(
        thread_id=THREAD_ID,
        action=tool_name,
        detail=str(tool_args)
    )
    print("📨 Notificación enviada a Telegram\n")

    decision = input("¿Aprobás la acción? (s/n): ").strip().lower()
    approved = decision == "s"

    result = resume_rca(thread_id=THREAD_ID, approved=approved)
    print("\n" + "=" * 60)
    print("RESULTADO FINAL:")
    print("=" * 60)
    print(result["messages"][-1].content)
else:
    print("El agente terminó sin requerir aprobación:")
    print(last_msg.content)