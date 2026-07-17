# server.py
from dotenv import load_dotenv
import json
from mcp.server.fastmcp import FastMCP
from nornir.core import Nornir
from nornir.core.plugins.connections import ConnectionPluginRegister
from nornir.plugins.runners import ThreadedRunner

ConnectionPluginRegister.auto_register()
from nornir_netmiko.tasks import netmiko_send_command
from nornir.core.task import Task, Result
from inventory_builder import build_inventory
from parsers import parse_interface_status, parse_bgp_summary

load_dotenv()

mcp = FastMCP("netops-server-v3")





def get_nornir() -> Nornir:
    """
    Inicializa y devuelve una instancia de Nornir 
    con la configuración de inventario.
    """
    inventory = build_inventory()
    return Nornir(
        inventory=inventory,
        runner=ThreadedRunner(num_workers=10),
    )


def run_on_all(command: str) -> dict:
    """
    Ejecuta un comando sobre todos los hosts en paralelo.
    Devuelve un dict: {hostname: output_string | error_string}
    """
    nr = get_nornir() # Cada llamada a run_on_all crea una nueva instancia de Nornir para asegurar fresh state y evitar problemas de concurrencia. 
    result = nr.run(task=netmiko_send_command, command_string=command)

    outputs = {}
    for host, host_result in result.items():
        if host_result[0].failed:
            outputs[host] = f"ERROR: {host_result[0].exception}"
        else:
            outputs[host] = host_result[0].result
    return outputs


@mcp.tool()
def get_all_interfaces() -> str:
    """
    Consulta el estado de interfaces en todos los dispositivos de la red en paralelo.
    Devuelve un objeto JSON con cada dispositivo como clave y su lista de interfaces como valor.
    Útil para obtener una vista completa del estado de la red de forma eficiente.
    """
    raw_outputs = run_on_all("show ip interface brief")

    result = {}
    for host, raw in raw_outputs.items():
        if raw.startswith("ERROR"):
            result[host] = {"error": raw}
        else:
            interfaces = parse_interface_status(raw)
            result[host] = [i.model_dump() for i in interfaces]

    return json.dumps(result, indent=2)


@mcp.tool()
def get_all_bgp() -> str:
    """
    Consulta el estado BGP en todos los dispositivos de la red en paralelo.
    Devuelve un objeto JSON con el resumen BGP de cada dispositivo.
    Útil para detectar sesiones caídas en toda la red de un solo llamado.
    """
    raw_outputs = run_on_all("show ip bgp summary")

    result = {}
    for host, raw in raw_outputs.items():
        if raw.startswith("ERROR"):
            result[host] = {"error": raw}
        else:
            summary = parse_bgp_summary(raw)
            result[host] = summary.model_dump()

    return json.dumps(result, indent=2)


if __name__ == "__main__":
    print("Iniciando netops-server-v3 (multi-host)...")
    mcp.run()