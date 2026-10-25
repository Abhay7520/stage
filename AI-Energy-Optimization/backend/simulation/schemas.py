from pydantic import BaseModel, ConfigDict


class VMState(BaseModel):
    id: str
    name: str
    cpu: float
    memory: float
    server_id: str | None


class ServerState(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    name: str
    cpu_capacity: float
    memory_capacity: float
    cpu_used: float
    memory_used: float
    vms: list[VMState]


class Snapshot(BaseModel):
    servers: list[ServerState]
    vms: list[VMState]
    metrics: dict[str, float | int]
    revision: int
    tick: int
    data_source: str
    history_count: int


class MutationResponse(BaseModel):
    success: bool
    state: Snapshot
