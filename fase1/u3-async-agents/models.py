# models.py
from pydantic import BaseModel
from typing import Optional


class InterfaceStatus(BaseModel):
    interface: str
    ip_address: Optional[str] = None
    status: str        # "up", "down", "admin down"
    protocol: str      # "up", "down"


class BGPNeighbor(BaseModel):
    neighbor: str
    version: int
    as_number: int
    state_or_prefixes: str   # puede ser "Idle", "Active" o un número de prefijos
    up_down: str


class BGPSummary(BaseModel):
    router_id: str
    local_as: int
    neighbors: list[BGPNeighbor]


class DeviceVersion(BaseModel):
    hostname: Optional[str] = None
    os_version: Optional[str] = None
    platform: Optional[str] = None
    raw: str             # siempre guardamos el output crudo como fallback
