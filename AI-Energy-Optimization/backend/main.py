"""Local research application. Use one worker for the shared simulation store."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.simulation.routes import router as simulation_router
from backend.intelligence.routes import router as intelligence_router
from backend.intelligence.legacy_routes import router as legacy_router
from backend.optimization.routes import router as optimization_router
from backend.reporting.routes import router as reporting_router

app = FastAPI(title="GridOpt AI Research API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(","),
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)
for router in [
    simulation_router,
    intelligence_router,
    optimization_router,
    reporting_router,
    legacy_router,
]:
    app.include_router(router)

from fastapi.exceptions import RequestValidationError
from backend.errors import validation_error_handler

app.add_exception_handler(RequestValidationError, validation_error_handler)
