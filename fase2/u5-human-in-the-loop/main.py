# main.py
from agent import run_rca, resume_rca
from langgraph.errors import GraphInterrupt

ALERT = """
Cliente: AS65005
Síntoma: El cliente reporta pérdida total de conectividad BGP.
Dispositivo afectado: dist-sw02 (10.10.20.178)
Hora del reporte: hace 5 minutos
"""

THREAD_ID = "incidente-001"

if __name__ == "__main__":
    print("=" * 60)
    print("NOC RCA Agent con Human-in-the-Loop")
    print("=" * 60)
    print(f"\nAlerta:\n{ALERT}")
    print("\nAnalizando...\n")

    try:
        result = run_rca(alert=ALERT, thread_id=THREAD_ID)

        last_msg = result["messages"][-1]

        # Verificar si el agente pausó esperando aprobación
        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
            tool_name = last_msg.tool_calls[0]["name"]
            tool_args = last_msg.tool_calls[0]["args"]
            print("=" * 60)
            print("⏸  AGENTE PAUSADO — esperando aprobación humana")
            print(f"   Acción pendiente: {tool_name}({tool_args})")
            print(f"   Thread ID: {THREAD_ID}")
            print("   Revisá Telegram para aprobar o rechazar.")
            print("=" * 60)
            print("\nPara reanudar manualmente:")
            print(f"  from agent import resume_rca")
            print(f"  resume_rca('{THREAD_ID}', approved=True)")
        else:
            print("=" * 60)
            print("DIAGNÓSTICO:")
            print("=" * 60)
            print(last_msg.content)

    except GraphInterrupt as e:
        print("=" * 60)
        print("⏸  AGENTE PAUSADO (GraphInterrupt)")
        print(f"   Thread ID: {THREAD_ID}")
        print("=" * 60)

    except Exception as e:
        print(f"Error inesperado: {type(e).__name__}: {e}")
        raise