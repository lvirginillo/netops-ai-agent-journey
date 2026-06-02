# inventory_builder.py
import os
from nornir.core.inventory import Inventory, Host, Hosts, Groups


def build_inventory(**kwargs) -> Inventory:
    """
    Nornir llama a esta función con kwargs internos — la firma debe aceptarlos.
    Las credenciales se leen desde variables de entorno.
    """
    user = os.getenv("DEVICE_USER")
    password = os.getenv("DEVICE_PASS")

    hosts = Hosts({
        "dist-sw01": Host(
            name="dist-sw01",
            hostname=os.getenv("SW01_HOST"),
            port=22,
            username=user,
            password=password,
            platform="cisco_nxos",
        ),
        "dist-sw02": Host(
            name="dist-sw02",
            hostname=os.getenv("SW02_HOST"),
            port=22,
            username=user,
            password=password,
            platform="cisco_nxos",
        ),
    })

    return Inventory(hosts=hosts, groups=Groups())