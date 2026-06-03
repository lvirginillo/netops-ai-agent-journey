# agent.py
from dotenv import load_dotenv
from typing import Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.prebuilt import ToolNode
from tools import NOC_TOOLS

load_dotenv()

# ── Estado del agente ────────────────────────────────────────────────────────

class NOCState(MessagesState):
    """
    Estado del agente NOC.
    MessagesState ya incluye messages: list[AnyMessage] con reducer add_messages.
    Agregamos campos específicos del dominio NOC.
    """
    alert: str       # alerta que disparó el agente
    severity: str    # P1-P4, lo determina el agente al finalizar


# ── LLM y tools ─────────────────────────────────────────────────────────────

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(NOC_TOOLS)

SYSTEM_PROMPT = """Sos un agente NOC especializado en diagnóstico de redes carrier-grade.

Tu tarea es analizar alertas de red, consultar el estado de los dispositivos usando las 
herramientas disponibles, y producir un diagnóstico con causa raíz y próximos pasos.

Proceso:
1. Analizá la alerta recibida
2. Consultá las herramientas necesarias para recopilar evidencia
3. Correlacioná los datos obtenidos
4. Determiná la causa raíz
5. Asigná severidad: P1 (servicio caído), P2 (degradación severa), P3 (degradación leve), P4 (informativo)
6. Producí un diagnóstico claro con próximos pasos concretos

Siempre justificá tu diagnóstico con la evidencia recopilada.
Respondé en español."""


# ── Nodos del grafo ──────────────────────────────────────────────────────────

def agent_node(state: NOCState) -> dict:
    """
    Nodo principal: el LLM analiza el estado y decide si llamar tools o terminar.
    Solo devuelve los mensajes nuevos — MessagesState los acumula automáticamente.
    """
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def should_continue(state: NOCState) -> Literal["tools", "end"]:
    """
    Edge condicional: si el último mensaje tiene tool_calls, ir a tools.
    Si no, el agente terminó — ir a end.
    """
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"


# ── Construcción del grafo ───────────────────────────────────────────────────

tool_node = ToolNode(NOC_TOOLS)

graph_builder = StateGraph(NOCState)

graph_builder.add_node("agent", agent_node)
graph_builder.add_node("tools", tool_node)

graph_builder.set_entry_point("agent")

graph_builder.add_conditional_edges(
    "agent",
    should_continue,
    {"tools": "tools", "end": END}
)

graph_builder.add_edge("tools", "agent")

noc_agent = graph_builder.compile()


# ── Función de entrada ───────────────────────────────────────────────────────

def run_rca(alert: str) -> dict:
    """
    Recibe una alerta y corre el agente de RCA.
    Devuelve el estado final con el diagnóstico.
    """
    from langchain_core.messages import HumanMessage

    initial_state = {
        "messages": [HumanMessage(content=f"ALERTA: {alert}")],
        "alert": alert,
        "severity": "",
    }

    final_state = noc_agent.invoke(initial_state)
    return final_state