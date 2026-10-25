import copy
import json
import math
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pytest
from fastapi.testclient import TestClient
from backend.simulation.store import SimulationStore
from backend.simulation.engine import SimulationError
from backend.intelligence.service import IntelligenceService, build_features
from backend.optimization.engine import (
    plan,
    apply,
    valid,
    evaluate,
    predictions,
    migration_schedule,
)
from backend.optimization.schemas import Options


def history(cpu=50, mem=60):
    return [
        {
            "cpu_util_percent": cpu + i,
            "mem_util_percent": mem + i,
            "net_in": 10,
            "net_out": 8,
            "disk_io_percent": 12,
        }
        for i in range(4)
    ]


def configured():
    s = SimulationStore()
    s.histories = {vid: history(30 + i * 5, 50 + i * 3) for i, vid in enumerate(s.vms)}
    s.provenance = {v: "synthetic" for v in s.vms}
    return s


class FixedModel:
    def __init__(self, value):
        self.value = value

    def predict(self, X):
        return [self.value]


def test_feature_contract():
    x = build_features(history())
    assert x.shape == (1, 20)
    assert x["cpu_util_percent"].iloc[0] == 53
    assert x["cpu_util_percent_lag_3"].iloc[0] == 50


@pytest.mark.parametrize("n", [0, 1, 3])
def test_short_history(n):
    with pytest.raises(ValueError):
        build_features(history()[:n])


def test_forecast_clamps_and_uses_allocated_units():
    svc = IntelligenceService(FixedModel(120), FixedModel(-1), "xgboost")
    f = svc.forecast_vm(configured().vms["VM1"], history())
    assert f["predicted_cpu_percent"] == 100
    assert f["estimated_cpu_demand_vcpu"] == 4
    assert f["estimated_memory_demand_gb"] == 0


def test_persistence_is_explicit():
    svc = IntelligenceService(strategy="persistence")
    f = svc.forecast_vm(configured().vms["VM1"], history())
    assert f["predicted_memory_percent"] == 63


def test_incomplete_aggregation_not_complete():
    svc = IntelligenceService(strategy="persistence")
    rows = svc.server_summaries(configured().get_state(), [])
    assert not rows[0]["complete"]


def test_failed_migration_keeps_state():
    s = configured()
    s.allocate_vm("VM6", "S3")
    previous = s._document()
    with pytest.raises(SimulationError):
        s.mutate("migrate", s.migrate_vm, "VM2", "S3")
    assert previous == s._document()


def test_persistent_restart_and_reset(tmp_path):
    path = tmp_path / "state.json"
    s = SimulationStore(path)
    s.mutate("allocate", s.allocate_vm, "VM6", "S3")
    t = SimulationStore(path)
    assert t.vms["VM6"]["server_id"] == "S3"
    assert t.revision == 1
    t.mutate("reset", t.reset_all)
    assert SimulationStore(path).vms["VM6"]["server_id"] is None


def test_transaction_rolls_back_all_fields(tmp_path):
    s = SimulationStore(tmp_path / "state.json")
    old = s._document()

    def bad():
        s.tick = 10
        s.histories["VM1"] = history()
        s.vms["VM1"]["server_id"] = "missing"

    with pytest.raises(SimulationError):
        s.mutate("bad", bad)
    assert s._document() == old


@pytest.mark.parametrize("strategy", ["predictive", "best_fit", "first_fit"])
def test_plans_cover_every_vm_and_respect_both_resources(strategy):
    s = configured()
    old = s._document()
    p = plan(s, Options(strategy=strategy))
    assert valid(p["allocation"], s)
    assert len(p["allocation"]) == len(s.vms)
    assert p["after"]["unassigned_vms"] == 0
    assert old == s._document()
    for row in p["after"]["servers"]:
        assert row["reserved_cpu"] <= s.servers[row["server_id"]]["cpu_capacity"]
        assert row["reserved_memory"] <= s.servers[row["server_id"]]["memory_capacity"]


def test_stale_preview_rejected():
    s = configured()
    p = plan(s, Options())
    s.mutate("create", s.create_vm, "EX", "extra", 1, 1)
    with pytest.raises(SimulationError, match="State changed"):
        apply(s, p["allocation"], p["revision"], Options())


def test_infeasible_plan_does_not_drop_vm():
    s = configured()
    s.create_vm("TOO_BIG", "large", 100, 200)
    with pytest.raises(SimulationError):
        plan(s, Options())


def test_apply_cannot_omit_running_vm():
    s = configured()
    with pytest.raises(SimulationError):
        apply(s, {"VM1": "S1"}, s.revision, Options())


def test_memory_binds_even_with_cpu_space():
    s = SimulationStore()
    s.servers = {
        "A": {"id": "A", "name": "a", "cpu_capacity": 100, "memory_capacity": 8}
    }
    s.vms = {"v": {"id": "v", "name": "v", "cpu": 1, "memory": 9, "server_id": None}}
    with pytest.raises(SimulationError):
        plan(s, Options())


def test_missing_history_conservative():
    s = SimulationStore()
    assert predictions(s)["VM1"] == (1, 1)
    assert set(plan(s, Options())["missing_histories"]) == set(s.vms)


def test_migration_energy_is_included():
    s = configured()
    p = plan(s, Options(strategy="first_fit"))
    m = p["after"]
    assert m["migration_energy_wh"] == m["migration_gb"] * 0.05
    assert m["total_energy_wh"] == m["energy_wh"] + m["migration_energy_wh"]


def test_cooldown_is_respected():
    s = configured()
    s.vms["VM6"]["server_id"] = "S3"
    s.last_migration = {v: 0 for v in s.vms}
    p = plan(s, Options())
    assert all(p["allocation"][vid] == v["server_id"] for vid, v in s.vms.items())


def test_cyclic_migrations_need_spare_capacity():
    s = SimulationStore()
    s.servers = {
        i: {"id": i, "name": i, "cpu_capacity": 1, "memory_capacity": 1}
        for i in ["a", "b"]
    }
    s.vms = {
        i: {"id": i, "name": i, "cpu": 1, "memory": 1, "server_id": sid}
        for i, sid in [("v1", "a"), ("v2", "b")]
    }
    with pytest.raises(SimulationError, match="temporary capacity"):
        migration_schedule({"v1": "b", "v2": "a"}, s)


def test_sleep_state_and_wh_units():
    s = SimulationStore()
    m = evaluate({}, s, predictions(s), Options(interval_minutes=60))
    assert m["power_w"] == 15
    assert m["energy_wh"] == 15
    assert m["active_servers"] == 0


def test_parallel_updates_serialized(tmp_path):
    s = SimulationStore(tmp_path / "state.json")

    def create(i):
        s.mutate("create", s.create_vm, f"x{i}", "x", 1, 1)

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(create, range(12)))
    assert s.revision == 12
    assert len(SimulationStore(tmp_path / "state.json").vms) == 18


@pytest.fixture
def client(tmp_path, monkeypatch):
    from backend.main import app
    import backend.simulation.routes as sr
    import backend.intelligence.routes as ir
    import backend.optimization.routes as op
    import backend.reporting.routes as rr

    s = SimulationStore(tmp_path / "state.json")
    for m in [sr, ir, op, rr]:
        monkeypatch.setattr(m, "simulator" if m is sr else "store", s)
    return TestClient(app), s


def test_full_api_workflow(client):
    c, s = client
    assert c.get("/health").status_code == 200
    assert c.get("/simulation/state").status_code == 200
    r = c.post(
        "/intelligence/forecast",
        json={"histories": {v: history() for v in s.vms}, "source": "synthetic"},
    )
    assert r.status_code == 200 and len(r.json()["vm_forecasts"]) == 6
    preview = c.post("/optimization/preview", json={}).json()
    assert len(preview["allocation"]) == 6
    assert (
        c.post(
            "/optimization/apply",
            json={"revision": preview["revision"], "allocation": preview["allocation"]},
        ).status_code
        == 200
    )
    assert (
        c.post(
            "/optimization/apply",
            json={"revision": preview["revision"], "allocation": preview["allocation"]},
        ).status_code
        == 409
    )
    assert c.post("/optimization/step", json={"source": "synthetic"}).status_code == 200
    assert c.get("/reports/snapshot").status_code == 200
    assert "text/csv" in c.get("/reports/comparison.csv").headers["content-type"]
    assert c.get("/optimization/history").json()["tick"] == 1


@pytest.mark.parametrize(
    "path,body,status",
    [
        ("/simulation/allocate", {"vm_id": "missing", "server_id": "S1"}, 404),
        (
            "/simulation/servers",
            {"id": "S1", "name": "duplicate", "cpu_capacity": 1, "memory_capacity": 1},
            409,
        ),
        ("/simulation/vms", {"id": "bad", "name": "bad", "cpu": -1, "memory": 2}, 422),
        ("/optimization/preview", {"interval_minutes": 0}, 422),
        ("/optimization/preview", {"strategy": "fake-ai"}, 422),
        ("/optimization/preview", {"idle_watts": 300, "peak_watts": 100}, 422),
        ("/intelligence/forecast", {"histories": {"UNKNOWN": history()}}, 404),
        ("/intelligence/forecast", {"histories": {"VM1": history()[:2]}}, 422),
        ("/optimization/apply", {"revision": 0, "allocation": {"VM1": "S1"}}, 409),
    ],
)
def test_api_validation(client, path, body, status):
    c, s = client
    before = s._document()
    r = c.post(path, json=body)
    assert r.status_code == status, r.text
    assert before == s._document()


def test_legacy_models_infer(client):
    c, _ = client
    assert (
        0
        <= c.post("/predict/workload", json={"history": history()}).json()[
            "predicted_cpu_utilization"
        ]
        <= 100
    )
    data = {
        "cpu_mean": 40,
        "cpu_max": 60,
        "cpu_min": 20,
        "cpu_std": 5,
        "cpu_median": 40,
        "cpu_frequency_ghz": 2.5,
        "memory_util_gb": 2,
        "sda_write_count_during_interval": 10,
        "sda_read_count_during_interval": 10,
    }
    r = c.post("/predict/energy", json=data)
    assert r.status_code == 200 and math.isfinite(r.json()["predicted_energy"])
    opt = {
        "current_cpu": 40,
        "predicted_workload": 50,
        **{
            k: v
            for k, v in data.items()
            if k
            in [
                "cpu_frequency_ghz",
                "memory_util_gb",
                "sda_write_count_during_interval",
                "sda_read_count_during_interval",
            ]
        },
    }
    r = c.post("/optimize", json=opt)
    assert r.status_code == 200
    assert r.json()["optimization"]["recommended_cpu"] >= 50


def test_comparison_uses_same_complete_workload(client):
    c, s = client
    before = s._document()
    r = c.post("/optimization/compare", json={})
    assert r.status_code == 200
    for row in r.json()["rows"]:
        if row["status"] == "ok":
            assert row["metrics"]["scheduled_vms"] == 6
    assert before == s._document()


def test_failed_adaptive_interval_rolls_back_histories_and_tick(client):
    c, s = client
    s.mutate("oversized_vm", s.create_vm, "TOO_BIG", "impossible", 1000, 1000)
    previous = s._document()
    r = c.post("/optimization/step", json={"source": "synthetic"})
    assert r.status_code == 409
    assert s._document() == previous


def test_reset_clears_history_and_provenance(client):
    c, s = client
    c.post(
        "/intelligence/forecast",
        json={"histories": {"VM1": history()}, "source": "synthetic"},
    )
    assert s.histories
    assert c.post("/simulation/reset").status_code == 200
    assert not s.histories and not s.provenance
    assert s.tick == 0


def test_cors_configuration(client):
    c, _ = client
    r = c.options(
        "/optimization/preview",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert r.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"


def test_nonfinite_capacity_rejected(client):
    c, s = client
    previous = s._document()
    r = c.post(
        "/simulation/servers",
        content='{"id":"BAD","name":"bad","cpu_capacity":NaN,"memory_capacity":2}',
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 422
    assert s._document() == previous


def test_manual_migration_updates_cooldown(client):
    c, s = client
    assert (
        c.post(
            "/simulation/migrate", json={"vm_id": "VM1", "server_id": "S2"}
        ).status_code
        == 200
    )
    assert s.last_migration["VM1"] == s.tick


@pytest.mark.parametrize("strategy", ["first_fit", "best_fit"])
def test_conventional_previews_respect_same_cooldown(strategy):
    s = configured()
    s.allocate_vm("VM6", "S3")
    s.last_migration = {v: 0 for v in s.vms}
    p = plan(s, Options(strategy=strategy))
    assert p["allocation"] == {v: vm["server_id"] for v, vm in s.vms.items()}
