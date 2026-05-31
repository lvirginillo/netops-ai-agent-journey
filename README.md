# netops-ai-agent-journey

Curso práctico: construcción de agentes de IA que operan infraestructura de red.

Combina automatización de redes (Nornir, Netmiko, Ansible) con IA agéntica (LangGraph, MCP) para crear herramientas NOC autónomas — desde el diseño de tools hasta el deploy con CI/CD.

---

## Stack

Python · LangGraph · MCP Protocol · Nornir · Netmiko · FastAPI · Docker · GitLab CI/CD · Prometheus · Grafana · Railway · Telegram

---

## Estructura del curso

### Fase 1 — Fundamentos: Agent Tools sobre infraestructura real
Convertir scripts de red en tools invocables por un agente.

| Unidad | Tema |
|--------|------|
| U1 | MCP Server para redes — Nornir/Netmiko como MCP tools |
| U2 | Structured outputs + validación Pydantic para datos de red |
| U3 | Agentes async con Nornir — consultas paralelas multi-equipo |

### Fase 2 — Agentic Workflows
Flujos multi-step que toman decisiones sobre el estado de la red.

| Unidad | Tema |
|--------|------|
| U4 | Agente de RCA — análisis de causa raíz con LangGraph |
| U5 | Human-in-the-loop — aprobación antes de ejecutar cambios |
| U6 | Multi-agente — NOC Supervisor + agentes especialistas |

### Fase 3 — CI/CD para agentes
Testing, pipelines y observabilidad para agentes de IA.

| Unidad | Tema |
|--------|------|
| U7 | Testing de agentes — mocks, pytest, LangSmith tracing |
| U8 | Pipeline CI/CD en GitLab para agentes LangGraph |
| U9 | Observabilidad — Prometheus + Grafana para salud del agente |

### Fase 4 — Deploy productivo y portfolio
Deploy seguro y demo pública.

| Unidad | Tema |
|--------|------|
| U10 | Deploy productivo — secrets, rate limiting, audit log |
| U11 | Demo portfolio — chat interactivo + sandbox DevNet |

---

## Progreso

| Fase | Estado |
|------|--------|
| Fase 1 | 🔜 En curso |
| Fase 2 | ⏳ Pendiente |
| Fase 3 | ⏳ Pendiente |
| Fase 4 | ⏳ Pendiente |

---

## Entorno de laboratorio

Todos los ejercicios usan [Cisco DevNet Sandboxes](https://devnetsandbox.cisco.com/) — gratuitos, reservables, sin hardware propio.

- **Always-On:** pruebas básicas de conectividad
- **Reservable (CML):** topología completa con Nexus 9000v / NX-OS

---

## Estructura del repositorio

```
netops-ai-agent-journey/
├── README.md
├── .gitignore
├── fase1/
│   ├── README.md
│   ├── u1-mcp-server/
│   ├── u2-structured-outputs/
│   └── u3-async-agents/
├── fase2/
│   ├── README.md
│   ├── u4-rca-agent/
│   ├── u5-human-in-the-loop/
│   └── u6-multi-agent/
├── fase3/
│   ├── README.md
│   ├── u7-testing/
│   ├── u8-cicd/
│   └── u9-observability/
└── fase4/
    ├── README.md
    ├── u10-deploy-productivo/
    └── u11-portfolio/
```

# Autor

Lautaro Virginillo linkedin.com/in/lautaro-virginillo
