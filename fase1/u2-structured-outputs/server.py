# server.py
from dotenv import load_dotenv
import os
import json
from mcp.server.fastmcp import FastMCP
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
from parsers import parse_interface_status, parse_bgp_summary, parse_version

load_dotenv()

mcp = FastMCP("netops-server-v2")


def get_device_config() -> dict:
    return {
        "device_type": os.getenv("DEVICE_TYPE"),
        "host":        os.getenv("DEVICE_HOST"),
        "port":        int(os.getenv("DEVICE_PORT", 22)),
        "username":    os.getenv("DEVICE_USER"),
        "password":    os.getenv("DEVICE_PASS"),
    }


def run_command(command: str) -> str:
    try:
        with ConnectHandler(**get_device_config()) as conn:
            return conn.send_command(command)
    except NetmikoTimeoutException:
        return f"ERROR: Timeout conectando a {os.getenv('DEVICE_HOST')}"
    except NetmikoAuthenticationException:
        return "ERROR: Fallo de autenticación"
    except Exception as e:
        return f"ERROR: {str(e)}"


@mcp.tool()
def get_interface_status() -> str:
    """
    Devuelve el estado de todas las interfaces IP del dispositivo.
    El resultado está estructurado: cada interfaz tiene nombre, IP, estado y protocolo.
    Útil para detectar interfaces caídas o sin IP asignada.
    """
    raw = run_command("show ip interface brief")
    if raw.startswith("ERROR"):
        return raw
    interfaces = parse_interface_status(raw)
    return json.dumps([i.model_dump() for i in interfaces], indent=2)


@mcp.tool()
def get_bgp_summary() -> str:
    """
    Devuelve el resumen BGP del dispositivo: router ID, AS local y estado de cada vecino.
    El resultado está estructurado por vecino con su estado (Idle, Active, Established).
    Útil para detectar sesiones BGP caídas o en estado incorrecto.
    """
    raw = run_command("show ip bgp summary")
    if raw.startswith("ERROR"):
        return raw
    summary = parse_bgp_summary(raw)
    return summary.model_dump_json(indent=2)


@mcp.tool()
def get_version() -> str:
    """
    Devuelve información de versión del dispositivo: hostname, plataforma y versión de SO.
    Útil para identificar el equipo y verificar conectividad básica.
    """
    raw = run_command("show version")
    if raw.startswith("ERROR"):
        return raw
    version = parse_version(raw)
    return version.model_dump_json(indent=2)


if __name__ == "__main__":
    print("Iniciando netops-server-v2...")
    mcp.run()