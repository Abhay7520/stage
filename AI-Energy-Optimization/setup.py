from pathlib import Path
from setuptools import find_packages, setup

ROOT = Path(__file__).parent
setup(
    name="gridopt-ai",
    version="2.0.0",
    description="Forecast-informed cloud data center research simulator",
    packages=find_packages(include=["backend*", "src*", "scripts*"]),
    python_requires=">=3.11",
    install_requires=[
        line.strip()
        for line in (ROOT / "requirements.txt").read_text().splitlines()
        if line.strip()
    ],
    extras_require={"test": ["pytest==9.1.1", "httpx==0.28.1"]},
)
