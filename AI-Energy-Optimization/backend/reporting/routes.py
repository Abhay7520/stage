import csv
import io
import json
from datetime import datetime, timezone
from fastapi import APIRouter
from fastapi.responses import Response
from backend.config import MODELS_DIR
from backend.simulation.store import store
from backend.optimization.routes import comparison, guarded
from backend.optimization.schemas import Options

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/evaluation")
def evaluation():
    result = {}
    for key, filename in [
        ("forecast", "forecast_evaluation.json"),
        ("energy", "energy_evaluation.json"),
    ]:
        path = MODELS_DIR / filename
        result[key] = (
            json.loads(path.read_text())
            if path.exists()
            else {"status": "Evaluation artifact unavailable"}
        )
    return result


@router.get("/snapshot")
def snapshot():
    def build():
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "state": store.get_state(),
            "sources": store.provenance,
            "comparison": comparison(store, Options()),
            "history": store.events,
            "evaluation": evaluation(),
            "limitations": [
                "Simulation only; no cloud control.",
                "Power, migration duration and SLA pressure are proxies, not measured cloud metrics.",
                "Base-paper code/protocol was not supplied: conventional baselines are not a reproduction.",
                "Aggregated workload file lacks timestamps and entity IDs.",
            ],
        }

    return guarded(build)


@router.get("/comparison.csv")
def comparison_csv():
    doc = guarded(lambda: comparison(store, Options()))
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "strategy",
            "status",
            "energy_wh",
            "migration_energy_wh",
            "total_energy_wh",
            "sla_pressure_proxy",
            "migrations",
            "active_servers",
            "energy_saving_percent",
        ],
    )
    writer.writeheader()
    for r in doc["rows"]:
        writer.writerow(
            {k: r.get(k, r.get("metrics", {}).get(k, "")) for k in writer.fieldnames}
        )
    return Response(
        output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="algorithm-comparison.csv"'
        },
    )
