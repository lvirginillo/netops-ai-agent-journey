# server.py
from dotenv import load_dotenv
import os
from mcp.server.fastmcp import FastMCP
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException

load_dotenv()

# --- Configuración del servidor ---
mcp = FastMCP("netops-server")

# --- Helper: conexión al dispositivo ---
def get_device_config() -> dict:
    """Devuelve la configuración del dispositivo desde variables de entorno."""
    return {
        "device_type": os.getenv("DEVICE_TYPE"),
        "host":        os.getenv("DEVICE_HOST"),
        "port":        int(os.getenv("DEVICE_PORT", 22)),
        "username":    os.getenv("DEVICE_USER"),
        "password":    os.getenv("DEVICE_PASS"),
    }

def run_command(command: str) -> str:
    """Conecta al dispositivo, ejecuta un comando y devuelve el output."""
    try:
        with ConnectHandler(**get_device_config()) as conn:
            return conn.send_command(command)
    except NetmikoTimeoutException:
        return f"ERROR: Timeout conectando a {os.getenv('DEVICE_HOST')}"
    except NetmikoAuthenticationException:
        return "ERROR: Fallo de autenticación"
    except Exception as e:
        return f"ERROR: {str(e)}"

# --- Tools ---

@mcp.tool()
def get_interface_status() -> str:
    """
    Devuelve el estado de todas las interfaces del dispositivo.
    Útil para detectar interfaces caídas o en estado erróneo.
    """
    return run_command("show ip interface brief")

@mcp.tool()
def get_bgp_neighbors() -> str:
    """
    Devuelve el estado de las sesiones BGP del dispositivo.
    Útil para verificar si hay vecinos caídos o en estado incorrecto.
    """
    return run_command("show ip bgp summary")

@mcp.tool()
def get_version() -> str:
    """
    Devuelve información de versión del sistema operativo del dispositivo.
    Útil para identificar el equipo y verificar conectividad básica.
    """
    return run_command("show version")

# --- Entry point ---
if __name__ == "__main__":
    print("Iniciando MCP Server netops-server...")
    mcp.run()