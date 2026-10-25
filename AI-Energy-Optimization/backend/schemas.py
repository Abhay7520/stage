from pydantic import BaseModel, Field


class ResourceData(BaseModel):
    model_config = {"allow_inf_nan": False}
    cpu_util_percent: float = Field(ge=0, le=100)

    mem_util_percent: float = Field(ge=0, le=100)

    net_in: float = Field(ge=0)

    net_out: float = Field(ge=0)

    disk_io_percent: float = Field(ge=0, le=100)


class WorkloadHistory(BaseModel):
    history: list[ResourceData] = Field(min_length=4, max_length=64)


class EnergyInput(BaseModel):
    model_config = {"allow_inf_nan": False}

    cpu_mean: float = Field(ge=0)

    cpu_max: float = Field(ge=0)

    cpu_min: float = Field(ge=0)

    cpu_std: float = Field(ge=0)

    cpu_median: float = Field(ge=0)

    cpu_frequency_ghz: float = Field(ge=0)

    memory_util_gb: float = Field(ge=0)

    sda_write_count_during_interval: float = Field(ge=0)

    sda_read_count_during_interval: float = Field(ge=0)


class OptimizationInput(BaseModel):
    model_config = {"allow_inf_nan": False}

    current_cpu: float = Field(ge=0, le=100)

    predicted_workload: float = Field(ge=0, le=100)

    cpu_frequency_ghz: float = Field(ge=0)

    memory_util_gb: float = Field(ge=0)

    sda_write_count_during_interval: float = Field(ge=0)

    sda_read_count_during_interval: float = Field(ge=0)
