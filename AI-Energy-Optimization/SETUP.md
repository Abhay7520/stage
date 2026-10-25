# Windows / VS Code setup

Tested here on Linux, Python 3.12.14 and Node 24.22.1. Windows-specific installation has not been executed. Use Python 3.12 (64-bit) and Node 24 LTS. Vite 8 needs a sufficiently recent Node version; Node 24 avoids older-runtime incompatibility.

## 1. Extract and open

Extract the ZIP into a normal writable folder. Open `AI-Energy-Optimization` in VS Code with **File → Open Folder**. The terminal must show the folder containing `backend`, `frontend`, `models` and `setup.py`.

## 2. Backend — PowerShell terminal 1

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e . --no-deps
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

If PowerShell prevents activation, use the interpreter directly instead of changing machine policies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Keep one backend process/worker. Models load from the project folder; start from this extracted checkout. The editable installation is intended for this checkout: data/model artifacts are not embedded into a standalone wheel.

Open <http://127.0.0.1:8000/health> and <http://127.0.0.1:8000/docs>.

## 3. Frontend — PowerShell terminal 2

```powershell
cd frontend
npm ci
Copy-Item .env.example .env
npm run dev -- --host 127.0.0.1
```

Open <http://127.0.0.1:5173>. If Vite selects a different port, stop the other process or configure `CORS_ORIGINS` to include the selected frontend origin.

The frontend `.env` is loaded by Vite. Restart Vite after changing `VITE_API_URL`. Backend `.env.example` documents settings; the backend does not implicitly load `.env`. Set optional overrides before starting it:

```powershell
$env:SIMULATION_STATE_PATH = "runtime/state.json"
$env:CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
```

State survives reloads and normal backend restarts in `runtime/state.json`. The simulator's Reset action deliberately resets topology, histories and decision history. To recover from an invalid/corrupt state file, stop the backend, retain a backup, then remove or rename that file to start from the demonstration configuration.

## 4. Verify

In the activated root terminal, stop the backend with Ctrl+C if necessary, then run:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

In `frontend`:

```powershell
npm run build
npm run lint
```

Optional isolated browser integration check, from the project root:

```powershell
python -m playwright install chromium
python -m scripts.verify_browser
```

It starts temporary test servers on 8011/5178 and uses a temporary state file. Those ports must be free. It does not reset the normal simulation state. Browser-download availability and Windows system/browser requirements depend on the local environment.

## 5. Reproduce models and experiments (optional)

From the activated root terminal:

```powershell
python train_memory.py
python -m scripts.train_energy_validated
python -m scripts.run_experiments
```

`train_memory.py` evaluates and saves **both** CPU and RAM models. Restart the backend after training because models are loaded once at startup. The original `train_workload.py`, `train_energy.py`, `analyze_vm.py`, `analyze_instance.py` and `optimize_resources.py` are retained for compatibility, but the validated scripts above define the new documented evaluation protocol. Original scripts can overwrite their historical artifact filenames; use the validated scripts for reproducing current results.

No API keys, database account or cloud subscription is required.

## Troubleshooting

- `ModuleNotFoundError`: install into the same Python interpreter VS Code is using. Prefer `python -m pip`.
- Frontend reports failed fetch: confirm `/health`, `VITE_API_URL`, backend port and CORS origin.
- Cannot place a VM: both its full vCPU and RAM reservations must fit; predictions do not permit overcommit. A bounded search failure can also reflect cooldown or lack of migration staging capacity.
- Stale preview: refresh the preview after any topology/history change or another apply operation.
- Results are conservative: enter histories for each VM; missing histories use 100% demand. Example histories are always labeled synthetic.
- Model output differs slightly: platform/package numeric differences may affect floating-point results. Full versions and result files are included.
