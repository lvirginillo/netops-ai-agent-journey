# netops-ai-agent-journey

Practical course: building AI agents that operate network infrastructure.

Combining network automation (Nornir, Netmiko, Ansible) with agentic AI (LangGraph, MCP) to create autonomous NOC tooling — from tool design to CI/CD deploy.

---

## Stack

Python · LangGraph · MCP Protocol · Nornir · Netmiko · FastAPI · Docker · GitLab CI/CD · Prometheus · Grafana · Railway · Telegram

---

## Course Structure

### Phase 1 — Foundations: Agent Tools on Real Infrastructure
Convert network scripts into agent-callable tools.

| Unit | Topic |
|------|-------|
| U1 | MCP Server for networks — Nornir/Netmiko as MCP tools |
| U2 | Structured outputs + Pydantic validation for network data |
| U3 | Async agents with Nornir — parallel multi-device queries |

### Phase 2 — Agentic Workflows
Multi-step flows that take decisions on network state.

| Unit | Topic |
|------|-------|
| U4 | RCA Agent — root cause analysis with LangGraph |
| U5 | Human-in-the-loop — approval before executing changes |
| U6 | Multi-agent — NOC Supervisor + Specialist agents |

### Phase 3 — CI/CD for Agents
Testing, pipelines and observability for AI agents.

| Unit | Topic |
|------|-------|
| U7 | Testing agents — mocks, pytest, LangSmith tracing |
| U8 | GitLab CI/CD pipeline for LangGraph agents |
| U9 | Observability — Prometheus + Grafana for agent health |

### Phase 4 — Production Deploy & Portfolio
Secure deploy and public demo.

| Unit | Topic |
|------|-------|
| U10 | Production deploy — secrets, rate limiting, audit log |
| U11 | Portfolio demo — interactive chat UI + DevNet sandbox |

---

## Progress

| Phase | Status |
|-------|--------|
| Phase 1 | 🔜 In progress |
| Phase 2 | ⏳ Pending |
| Phase 3 | ⏳ Pending |
| Phase 4 | ⏳ Pending |

---

## Lab Environment

All exercises use [Cisco DevNet Sandboxes](https://devnetsandbox.cisco.com/) — free, reservable, no hardware required.

- **Always-On:** basic connectivity tests
- **Reservable (CML):** full topology with Nexus 9000v / NX-OS

---

## Repository Structure

```
netops-ai-agent-journey/
├── README.md
├── .gitignore
├── phase1/
│   ├── README.md
│   ├── u1-mcp-server/
│   ├── u2-structured-outputs/
│   └── u3-async-agents/
├── phase2/
│   ├── README.md
│   ├── u4-rca-agent/
│   ├── u5-human-in-the-loop/
│   └── u6-multi-agent/
├── phase3/
│   ├── README.md
│   ├── u7-testing/
│   ├── u8-cicd/
│   └── u9-observability/
└── phase4/
    ├── README.md
    ├── u10-production/
    └── u11-portfolio/
```
