from typing import Literal
from pydantic import BaseModel, Field, model_validator


class Options(BaseModel):
    model_config = {"allow_inf_nan": False, "extra": "forbid"}
    strategy: Literal["predictive", "first_fit", "best_fit", "static"] = "predictive"
    interval_minutes: float = Field(default=5, gt=0, le=1440)
    energy_weight: float = Field(default=1, ge=0, le=10)
    risk_weight: float = Field(default=2, ge=0, le=10)
    balance_weight: float = Field(default=0.15, ge=0, le=10)
    migration_weight: float = Field(default=0.4, ge=0, le=10)
    headroom: float = Field(default=0.10, ge=0, le=0.5)
    cooldown_intervals: int = Field(default=2, ge=0, le=100)
    minimum_improvement: float = Field(default=0.002, ge=0, le=1)
    idle_watts: float = Field(default=100, gt=0, le=10000)
    peak_watts: float = Field(default=250, gt=0, le=20000)
    sleep_watts: float = Field(default=5, ge=0, le=1000)
    migration_wh_per_gb: float = Field(default=0.05, ge=0, le=10)
    beam_width: int = Field(default=32, ge=1, le=128)

    @model_validator(mode="after")
    def power_profile_order(self):
        if not self.sleep_watts <= self.idle_watts <= self.peak_watts:
            raise ValueError("Require sleep watts <= idle watts <= peak watts.")
        return self


class ApplyRequest(Options):
    revision: int = Field(ge=0)
    allocation: dict[str, str]


class StepRequest(Options):
    source: Literal["unchanged", "synthetic"] = "unchanged"
    seed: int = Field(default=42, ge=0, le=2147483647)


class MetricResponse(BaseModel):
    model_config = {"extra": "allow", "allow_inf_nan": False}
    total_energy_wh: float
    energy_wh: float
    migration_energy_wh: float
    power_w: float
    sla_pressure_proxy: float
    scheduled_vms: int
    migrations: int
    servers: list[dict]


class PlanResponse(BaseModel):
    model_config = {"extra": "allow", "allow_inf_nan": False}
    revision: int
    tick: int
    strategy: str
    allocation: dict[str, str]
    before: MetricResponse
    after: MetricResponse
    actions: list[dict]
    explanation: str
    comparable_workload: bool
    missing_histories: list[str]
