# agent.py
import os
from dotenv import load_dotenv
from typing import Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from tools import NOC_TOOLS, ACTION_TOOLS


load_dotenv()


# ── Estado ───────────────────────────────────────────────────────────────────

class NOCState(MessagesState):
    alert: str
    severity: str
    pending_action: str    # acción que está esperando aprobación
    approved: bool         # True = aprobada, False = rechazada


# ── LLM ──────────────────────────────────────────────────────────────────────

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(NOC_TOOLS)

SYSTEM_PROMPT = """Sos un agente NOC especializado en diagnóstico y remediación de redes carrier-grade.

Tu tarea es:
1. Analizar la alerta recibida
2. Consultar el estado de los dispositivos con las herramientas de lectura disponibles
3. Diagnosticar la causa raíz
4. Si el diagnóstico confirma una sesión BGP caída en estado Idle, DEBÉS invocar reset_bgp_neighbor
   con la IP del vecino afectado. No describas la acción en texto — ejecutala con la tool.
5. Asignar severidad: P1 (servicio caído), P2 (degradación severa), P3 (degradación leve), P4 (informativo)

IMPORTANTE: Las tools de acción (reset_bgp_neighbor) requieren aprobación humana antes de ejecutarse.
El sistema pausará automáticamente para solicitar aprobación.

Respondé en español."""


# ── Nodos ────────────────────────────────────────────────────────────────────

def agent_node(state: NOCState) -> dict:
    """Nodo principal: el LLM analiza y decide."""
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def notify_and_wait_node(state: NOCState) -> dict:
    """
    Este nodo nunca se ejecuta directamente — el interrupt_before lo intercepta.
    Existe en el grafo para que el edge condicional pueda apuntar a él.
    """
    last_message = state["messages"][-1]
    tool_call = last_message.tool_calls[0]
    return {
        "pending_action": f"{tool_call['name']}({tool_call['args']})",
    }


# ── Edge condicional ─────────────────────────────────────────────────────────

def should_continue(state: NOCState) -> Literal["read_tools", "notify_and_wait", "end"]:
    """
    Decide el siguiente nodo basándose en el tipo de tool que el LLM quiere llamar.
    - Si es una tool de lectura → ejecutar directamente
    - Si es una tool de acción → notificar y esperar aprobación
    - Si no hay tool_calls → terminar
    """
    last_message = state["messages"][-1]

    if not (hasattr(last_message, "tool_calls") and last_message.tool_calls):
        return "end"

    tool_name = last_message.tool_calls[0]["name"]
    action_tool_names = [t.name for t in ACTION_TOOLS]

    if tool_name in action_tool_names:
        return "notify_and_wait"
    return "read_tools"


# ── Construcción del grafo ───────────────────────────────────────────────────

from tools import READ_TOOLS
read_tool_node = ToolNode(READ_TOOLS)
action_tool_node = ToolNode(ACTION_TOOLS)

checkpointer = MemorySaver()

graph_builder = StateGraph(NOCState)

graph_builder.add_node("agent", agent_node)
graph_builder.add_node("read_tools", read_tool_node)
graph_builder.add_node("notify_and_wait", notify_and_wait_node)
graph_builder.add_node("action_tools", action_tool_node)

graph_builder.set_entry_point("agent")

graph_builder.add_conditional_edges(
    "agent",
    should_continue,
    {
        "read_tools": "read_tools",
        "notify_and_wait": "notify_and_wait",
        "end": END
    }
)

graph_builder.add_edge("read_tools", "agent")
graph_builder.add_edge("notify_and_wait", "action_tools")
graph_builder.add_edge("action_tools", "agent")

noc_agent = graph_builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["notify_and_wait"],  # pausa ANTES de notificar
)


# ── Función de entrada ───────────────────────────────────────────────────────

def run_rca(alert: str, thread_id: str) -> dict:
    """Inicia el agente con una alerta. Puede pausar esperando aprobación."""
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {
        "messages": [HumanMessage(content=f"ALERTA: {alert}")],
        "alert": alert,
        "severity": "",
        "pending_action": "",
        "approved": False,
    }
    return noc_agent.invoke(initial_state, config=config)


def resume_rca(thread_id: str, approved: bool) -> dict:
    """
    Reanuda un agente pausado con la decisión del operador.
    """
    config = {"configurable": {"thread_id": thread_id}}

    if approved:
        return noc_agent.invoke(None, config=config)
    else:
        # Recuperar el estado actual para obtener el tool_call_id pendiente
        state = noc_agent.get_state(config)
        last_msg = state.values["messages"][-1]
        tool_call_id = last_msg.tool_calls[0]["id"]

        # Inyectar ToolMessage de cancelación + HumanMessage explicando el rechazo
        from langchain_core.messages import ToolMessage
        return noc_agent.invoke(
            {
                "messages": [
                    ToolMessage(
                        content="Acción cancelada por el operador.",
                        tool_call_id=tool_call_id,
                    ),
                    HumanMessage(
                        content="Acción rechazada. No ejecutar. Documentar el incidente y proponer alternativas manuales."
                    ),
                ]
            },
            config=config,
        )