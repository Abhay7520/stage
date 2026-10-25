from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.schemas import ResourceData
from backend.simulation.store import store
from backend.intelligence.service import service

router = APIRouter(prefix="/intelligence", tags=["Workload intelligence"])


class Histories(BaseModel):
    histories: dict[str, list[ResourceData]]
    source: str = Field(
        default="user-entered", pattern=r"^(user-entered|measured|synthetic)$"
    )


def forecast_all():
    forecasts = [
        service.forecast_vm(v, store.histories[v["id"]])
        for v in store.vms.values()
        if v["id"] in store.histories
    ]
    return {
        "vm_forecasts": forecasts,
        "server_forecasts": service.server_summaries(store.get_state(), forecasts),
        "missing_vm_ids": [v for v in store.vms if v not in store.histories],
        "sources": store.provenance,
        "summary": {
            "total_vms": len(forecasts),
            "high_risk_vms": sum(f["resource_risk"] != "Normal" for f in forecasts),
        },
    }


@router.get("/forecasts")
def forecasts():
    with store.lock:
        return forecast_all()


@router.get("/histories")
def histories():
    with store.lock:
        return {"histories": store.histories, "sources": store.provenance}


@router.post("/forecast")
def save_forecast(data: Histories):
    with store.lock:
        unknown = set(data.histories) - set(store.vms)
        if unknown:
            raise HTTPException(404, f"Unknown VMs: {sorted(unknown)}")
        try:
            for vid, history in data.histories.items():
                service.forecast_vm(store.vms[vid], history)

            def save():
                for vid, history in data.histories.items():
                    store.histories[vid] = [row.model_dump() for row in history[-64:]]
                    store.provenance[vid] = data.source

            store.mutate("save_workload_history", save)
            return forecast_all()
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
