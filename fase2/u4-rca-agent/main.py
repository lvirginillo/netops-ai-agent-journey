# main.py
from agent import run_rca

# Alerta de prueba — simula lo que llegaría de un sistema de monitoreo
ALERT = """
Cliente: AS65005
Síntoma: El cliente reporta pérdida total de conectividad BGP.
Dispositivo afectado: dist-sw02 (10.10.20.178)
Hora del reporte: hace 5 minutos
"""

if __name__ == "__main__":
    print("=" * 60)
    print("NOC RCA Agent")
    print("=" * 60)
    print(f"\nAlerta recibida:\n{ALERT}")
    print("\nAnalizando...\n")

    result = run_rca(ALERT)

    # El diagnóstico está en el último mensaje del agente
    last_message = result["messages"][-1]
    print("=" * 60)
    print("DIAGNÓSTICO:")
    print("=" * 60)
    print(last_message.content)