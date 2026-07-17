# tools.py
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException

load_dotenv()


def _get_device_config() -> dict:
    return {
        "device_type": os.getenv("DEVICE_TYPE"),
        "host":        os.getenv("DEVICE_HOST"),
        "port":        int(os.getenv("DEVICE_PORT", 22)),
        "username":    os.getenv("DEVICE_USER"),
        "password":    os.getenv("DEVICE_PASS"),
    }


def _run_command(command: str) -> str:
    try:
        with ConnectHandler(**_get_device_config()) as conn:
            return conn.send_command(command)
    except NetmikoTimeoutException:
        return f"ERROR: Timeout conectando a {os.getenv('DEVICE_HOST')}"
    except NetmikoAuthenticationException:
        return "ERROR: Fallo de autenticación"
    except Exception as e:
        return f"ERROR: {str(e)}"


def _run_config_command(commands: list[str]) -> str:
    """Ejecuta comandos en modo configuración."""
    try:
        with ConnectHandler(**_get_device_config()) as conn:
            output = conn.send_config_set(commands)
            return output
    except Exception as e:
        return f"ERROR: {str(e)}"


@tool
def get_interface_status() -> str:
    """
    Devuelve el estado de todas las interfaces IP del dispositivo.
    Usar cuando se sospechan interfaces caídas o sin IP asignada.
    """
    return _run_command("show ip interface brief")


@tool
def get_bgp_summary() -> str:
    """
    Devuelve el resumen BGP: router ID, AS local y estado de cada vecino.
    Usar cuando se sospecha pérdida de conectividad por sesiones BGP caídas.
    """
    return _run_command("show ip bgp summary")


@tool
def reset_bgp_neighbor(neighbor_ip: str) -> str:
    """
    Resetea la sesión BGP con un vecino específico usando 'clear ip bgp'.
    ATENCIÓN: Esta acción modifica el estado de la red. Requiere aprobación humana.
    Usar solo cuando el diagnóstico confirma que la sesión BGP está caída y no levanta sola.
    Args:
        neighbor_ip: dirección IP del vecino BGP a resetear, por ejemplo '10.10.10.1'
    """
    return _run_command(f"clear ip bgp {neighbor_ip} soft")


# Tools de solo lectura — no requieren aprobación
READ_TOOLS = [get_interface_status, get_bgp_summary]

# Tools de acción — requieren aprobación humana antes de ejecutarse
ACTION_TOOLS = [reset_bgp_neighbor]

# Todas las tools
NOC_TOOLS = READ_TOOLS + ACTION_TOOLS