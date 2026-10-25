"""Starts isolated backend/frontend servers; never resets the normal runtime state."""

import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from scripts.browser_smoke import main

ROOT = Path(__file__).resolve().parents[1]


def run():
    with tempfile.TemporaryDirectory() as d:
        env = {
            **os.environ,
            "SIMULATION_STATE_PATH": str(Path(d) / "state.json"),
            "CORS_ORIGINS": "http://127.0.0.1:5178",
            "VITE_API_URL": "http://127.0.0.1:8011",
        }
        api = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "backend.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8011",
            ],
            cwd=ROOT,
            env=env,
            stdout=subprocess.DEVNULL,
        )
        front = subprocess.Popen(
            [
                shutil.which("npm"),
                "run",
                "dev",
                "--",
                "--host",
                "127.0.0.1",
                "--port",
                "5178",
                "--strictPort",
            ],
            cwd=ROOT / "frontend",
            env=env,
            stdout=subprocess.DEVNULL,
        )
        try:
            for url in ["http://127.0.0.1:8011/health", "http://127.0.0.1:5178"]:
                for attempt in range(60):
                    try:
                        urllib.request.urlopen(url, timeout=1)
                        break
                    except Exception:
                        if attempt == 59:
                            raise RuntimeError("Test server did not start: " + url)
                        time.sleep(0.2)
            main()
        finally:
            for proc in [front, api]:
                proc.terminate()
            for proc in [front, api]:
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()


if __name__ == "__main__":
    run()
