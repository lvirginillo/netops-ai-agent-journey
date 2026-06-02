# parsers.py
import re
from models import InterfaceStatus, BGPNeighbor, BGPSummary, DeviceVersion


def parse_interface_status(raw: str) -> list[InterfaceStatus]:
    """
    Parsea el output de 'show ip interface brief' en NX-OS.
    Formato: <iface> <ip|unassigned> protocol-X/link-X/admin-X
    """
    interfaces = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("IP Interface") or line.startswith("Interface"):
            continue
        parts = line.split()
        if len(parts) < 3:
            continue

        # Extraer link y protocol del campo "protocol-up/link-up/admin-up"
        link_status = "unknown"
        protocol_status = "unknown"
        for segment in parts[2].split("/"):
            if segment.startswith("link-"):
                link_status = segment[5:]
            elif segment.startswith("protocol-"):
                protocol_status = segment[9:]

        interfaces.append(InterfaceStatus(
            interface=parts[0],
            ip_address=parts[1] if parts[1] != "unassigned" else None,
            status=link_status,
            protocol=protocol_status,
        ))
    return interfaces


def parse_bgp_summary(raw: str) -> BGPSummary:
    """
    Parsea el output de 'show ip bgp summary' en NX-OS.
    Devuelve BGPSummary con lista de vecinos.
    """
    router_id = "unknown"
    local_as = 0
    neighbors = []

    for line in raw.splitlines():
        # Extraer router ID y AS local
        if "BGP router identifier" in line:
            match = re.search(
                r"BGP router identifier (\S+), local AS number (\d+)", line
            )
            if match:
                router_id = match.group(1)
                local_as = int(match.group(2))

        # Parsear filas de vecinos (empiezan con una IP)

        """Neighbor   V   AS   MsgRcvd  MsgSent  TblVer  InQ  OutQ  Up/Down    State/PfxRcd
        10.10.10.1 4   0    0        0        0       0    0     00:08:47   Idle
        índice:    [0] [1]  [2]      [3]      [4]     [5]  [6]   [7]        [8]      [9]"""
        parts = line.split()
        if len(parts) >= 10:  # Aseguramos que hay suficientes columnas 
            try:
                # Validar que el primer campo sea una IP
                octets = parts[0].split(".")
                if len(octets) == 4 and all(o.isdigit() for o in octets):
                    neighbors.append(BGPNeighbor(
                        neighbor=parts[0],
                        version=int(parts[1]),
                        as_number=int(parts[2]) if parts[2].isdigit() else 0,
                        up_down=parts[8],           # era [7]
                        state_or_prefixes=parts[9], # era [8]
                    ))
            except (ValueError, IndexError):
                continue

    return BGPSummary(
        router_id=router_id,
        local_as=local_as,
        neighbors=neighbors,
    )


def parse_version(raw: str) -> DeviceVersion:
    """
    Parsea el output de 'show version' en NX-OS.
    Devuelve DeviceVersion con los campos más relevantes.
    """
    hostname = None
    os_version = None
    platform = None

    for line in raw.splitlines():
        if line.strip().startswith("Cisco Nexus"):
            platform = line.strip()
        if "system:" in line.lower() and "version" in line.lower():
            parts = line.split()
            if len(parts) >= 3:
                os_version = parts[-1]
        if "Device name:" in line:
            hostname = line.split(":")[-1].strip()

    return DeviceVersion(
        hostname=hostname,
        os_version=os_version,
        platform=platform,
        raw=raw,
    )