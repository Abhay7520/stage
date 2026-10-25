from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


MODELS_DIR = PROJECT_ROOT / "models"


ENERGY_MODEL_PATH = MODELS_DIR / "energy_model.json"


WORKLOAD_MODEL_PATH = MODELS_DIR / "workload_model.json"
