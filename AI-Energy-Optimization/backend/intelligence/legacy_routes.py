from fastapi import APIRouter, HTTPException
from backend.schemas import WorkloadHistory, EnergyInput, OptimizationInput
from backend.model_service import ModelService

router = APIRouter(tags=["Original model laboratory"])
model_service = ModelService()


@router.get("/")
def root():

    return {"message": "AI Energy Optimization API is running.", "status": "online"}


# =========================================
# HEALTH CHECK
# =========================================


@router.get("/health")
def health():

    return {
        "status": "healthy",
        "energy_model": "loaded",
        "workload_model": "loaded",
        "forecast_strategies": __import__(
            "backend.intelligence.service", fromlist=["service"]
        ).service.strategies,
    }


# =========================================
# WORKLOAD PREDICTION
# =========================================


@router.post("/predict/workload")
def predict_workload(data: WorkloadHistory):

    try:

        prediction = model_service.predict_workload(data.history)

        return {
            "success": True,
            "predicted_cpu_utilization": prediction,
            "unit": "percent",
        }

    except Exception as e:

        raise HTTPException(status_code=400, detail=str(e))


# =========================================
# ENERGY PREDICTION
# =========================================


@router.post("/predict/energy")
def predict_energy(data: EnergyInput):

    try:

        prediction = model_service.predict_energy(data)

        return {"success": True, "predicted_energy": prediction, "unit": "joules"}

    except Exception as e:

        raise HTTPException(status_code=400, detail=str(e))


# =========================================
# RESOURCE OPTIMIZATION
# =========================================


@router.post("/optimize")
def optimize_resources(data: OptimizationInput):

    try:

        result = model_service.optimize_resources(data)

        return {"success": True, "optimization": result}

    except Exception as e:

        raise HTTPException(status_code=400, detail=str(e))
