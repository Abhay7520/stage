"""Single-process persistent simulation with serialized, rollback-safe mutations."""

import copy
import json
import os
from pathlib import Path
from threading import RLock
from backend.config import PROJECT_ROOT
from backend.simulation.engine import DataCenterSimulator, SimulationError


class SimulationStore(DataCenterSimulator):
    def __init__(self, path=None):
        super().__init__()
        self.lock = RLock()
        self.path = Path(path) if path else None
        self.revision = 0
        self.tick = 0
        self.histories = {}
        self.provenance = {}
        self.events = []
        self.last_migration = {}
        if self.path and self.path.exists():
            self._restore(json.loads(self.path.read_text()))
            self.validate()

    def _document(self):
        return copy.deepcopy(
            {
                k: getattr(self, k)
                for k in (
                    "servers",
                    "vms",
                    "revision",
                    "tick",
                    "histories",
                    "provenance",
                    "events",
                    "last_migration",
                )
            }
        )

    def _restore(self, doc):
        for k, value in doc.items():
            if k in (
                "servers",
                "vms",
                "revision",
                "tick",
                "histories",
                "provenance",
                "events",
                "last_migration",
            ):
                setattr(self, k, value)

    def validate(self):
        for vm in self.vms.values():
            if vm["server_id"] is not None and vm["server_id"] not in self.servers:
                raise SimulationError("Unknown server in placement.", 409)
        for sid, server in self.servers.items():
            cpu, mem = self._usage(sid)
            if (
                cpu > server["cpu_capacity"] + 1e-9
                or mem > server["memory_capacity"] + 1e-9
            ):
                raise SimulationError(
                    "CPU or memory reservation exceeds capacity.", 409
                )

    def mutate(self, kind, operation, *args):
        with self.lock:
            previous = self._document()
            try:
                result = operation(*args)
                self.validate()
                for vid, vm in self.vms.items():
                    old = previous["vms"].get(vid, {}).get("server_id")
                    if old and old != vm["server_id"]:
                        self.last_migration[vid] = self.tick
                self.revision += 1
                self.events.append(
                    {"revision": self.revision, "tick": self.tick, "action": kind}
                )
                if self.path:
                    self.path.parent.mkdir(parents=True, exist_ok=True)
                    tmp = self.path.with_suffix(".tmp")
                    tmp.write_text(
                        json.dumps(self._document(), allow_nan=False, indent=2)
                    )
                    os.replace(tmp, self.path)
                return result
            except Exception:
                self._restore(previous)
                raise

    def reset_all(self):
        super().reset()
        self.histories = {}
        self.provenance = {}
        self.last_migration = {}
        self.tick = 0
        self.events = []
        return self.get_state()

    def get_state(self):
        with self.lock:
            return {
                **self._snapshot(),
                "revision": self.revision,
                "tick": self.tick,
                "data_source": "simulation",
                "history_count": len(self.histories),
            }


store = SimulationStore(
    os.environ.get("SIMULATION_STATE_PATH", str(PROJECT_ROOT / "runtime/state.json"))
)
