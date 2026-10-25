import { Explained } from "../../components/help/Help";
import { Metric, ResourceBar } from "./components/SimulationControls";

import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import {
  Server,
  Cpu,
  HardDrive,
  RefreshCw,
  Plus,
  MoveRight,
  AlertTriangle,
} from "lucide-react";

import { simulationApi } from "../../services/simulationApi";
import type {
  SimulationState,
  ServerCreate,
  VMCreate,
} from "../../types/simulation";

import "./DataCenterSimulator.css";

export default function SimulationPage() {
  const [state, setState] = useState<SimulationState | null>(null);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  const [allocation, setAllocation] = useState({
    vm_id: "",
    server_id: "",
  });

  const [migration, setMigration] = useState({
    vm_id: "",
    server_id: "",
  });

  const [newServer, setNewServer] = useState<ServerCreate>({
    id: "",
    name: "",
    cpu_capacity: 16,
    memory_capacity: 32,
  });

  const [newVM, setNewVM] = useState<VMCreate>({
    id: "",
    name: "",
    cpu: 2,
    memory: 4,
  });

  useEffect(() => {
    let active = true;

    simulationApi
      .state()
      .then((result) => {
        if (active) setState(result);
      })
      .catch((err: unknown) => {
        if (active) {
          setError(
            err instanceof Error ? err.message : "Failed to load simulation.",
          );
        }
      });

    return () => {
      active = false;
    };
  }, []);

  async function perform(
    action: () => Promise<{
      success: boolean;
      state: SimulationState;
    }>,
    successMessage: string,
  ) {
    setBusy(true);
    setError("");
    setMessage("");

    try {
      const result = await action();
      setState(result.state);
      setMessage(successMessage);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Operation failed.");
    } finally {
      setBusy(false);
    }
  }

  async function addServer(event: FormEvent) {
    event.preventDefault();

    const id = newServer.id.trim();
    const name = newServer.name.trim();

    if (!id || !name) {
      setError("Server ID and name are required.");
      return;
    }

    await perform(
      () =>
        simulationApi.createServer({
          ...newServer,
          id,
          name,
        }),
      "Physical server created successfully.",
    );
  }

  async function addVM(event: FormEvent) {
    event.preventDefault();

    const id = newVM.id.trim();
    const name = newVM.name.trim();

    if (!id || !name) {
      setError("VM ID and name are required.");
      return;
    }

    await perform(
      () =>
        simulationApi.createVM({
          ...newVM,
          id,
          name,
        }),
      "VM created. You can now allocate it.",
    );
  }

  if (!state) {
    return (
      <div className="sim-page">
        <h2>Virtual Data Center</h2>
        <p>{error || "Loading simulation..."}</p>
        {error && (
          <Explained action title="Retry">
            <button onClick={() => window.location.reload()}>Retry</button>
          </Explained>
        )}
      </div>
    );
  }

  const unassignedVMs = state.vms.filter((vm) => vm.server_id === null);

  const assignedVMs = state.vms.filter((vm) => vm.server_id !== null);

  const metrics = state.metrics;

  return (
    <section className="sim-page">
      <div className="sim-heading">
        <div>
          <span className="eyebrow">PHASE 6 — SIMULATION ENGINE</span>
          <h2>Virtual Data Center</h2>
          <p>
            Manage physical servers, allocate virtual machines, and simulate
            resource migration.
          </p>
        </div>

        <Explained action title="Reset Simulation">
          <button
            type="button"
            className="sim-button"
            disabled={busy}
            onClick={() =>
              perform(simulationApi.reset, "Simulation reset successfully.")
            }
          >
            <RefreshCw size={16} />
            Reset Simulation
          </button>
        </Explained>
      </div>

      {error && <div className="sim-notice sim-error">{error}</div>}

      {message && <div className="sim-notice sim-success">{message}</div>}

      <div className="sim-stats">
        <Metric
          label="Physical Servers"
          value={metrics.total_servers.toString()}
        />

        <Metric label="Virtual Machines" value={metrics.total_vms.toString()} />

        <Metric
          label="Allocated CPU"
          value={`${metrics.used_cpu} / ${metrics.total_cpu}`}
        />

        <Metric
          label="Allocated Memory"
          value={`${metrics.used_memory} / ${metrics.total_memory} GB`}
        />
      </div>

      <div className="sim-stats">
        <Metric
          label="CPU Allocation"
          value={`${metrics.cpu_utilization_percent}%`}
        />

        <Metric
          label="Memory Allocation"
          value={`${metrics.memory_utilization_percent}%`}
        />

        <Metric
          label="Unassigned VMs"
          value={metrics.unassigned_vms.toString()}
        />

        <Metric
          label="High Allocation Servers"
          value={metrics.high_utilization_servers.toString()}
        />
      </div>

      <h3 className="sim-section-title">Physical Infrastructure</h3>

      <div className="sim-server-grid">
        {state.servers.map((server) => (
          <article key={server.id} className="sim-server">
            <div className="sim-server-heading">
              <Server size={22} />

              <div>
                <h3>{server.name}</h3>
                <small>{server.id}</small>
              </div>

              {server.status === "high" && (
                <span className="sim-warning">
                  <AlertTriangle size={13} />
                  High
                </span>
              )}
            </div>

            <ResourceBar
              label="Allocated CPU"
              used={server.cpu_used}
              total={server.cpu_capacity}
              unit="vCPU"
            />

            <ResourceBar
              label="Allocated Memory"
              used={server.memory_used}
              total={server.memory_capacity}
              unit="GB"
            />

            <div className="sim-vm-list">
              <h4>Assigned VMs ({server.vms.length})</h4>

              {server.vms.length === 0 && (
                <p className="sim-empty">No virtual machines assigned.</p>
              )}

              {server.vms.map((vm) => (
                <div key={vm.id} className="sim-vm">
                  <div>
                    <strong>{vm.name}</strong>
                    <small>{vm.id}</small>
                  </div>

                  <div className="sim-vm-resources">
                    <span>
                      <Cpu size={13} />
                      {vm.cpu} vCPU
                    </span>

                    <span>
                      <HardDrive size={13} />
                      {vm.memory} GB
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </article>
        ))}
      </div>

      <div className="sim-forms">
        <section className="sim-panel">
          <h3>Allocate VM</h3>
          <p>
            Assign an unallocated VM to a physical server with sufficient
            capacity.
          </p>

          <Explained title="VM">
            <select
              aria-label="VM"
              value={allocation.vm_id}
              onChange={(event) =>
                setAllocation({
                  ...allocation,
                  vm_id: event.target.value,
                })
              }
            >
              <option value="">Select VM</option>
              {unassignedVMs.map((vm) => (
                <option key={vm.id} value={vm.id}>
                  {vm.id} — {vm.name}
                </option>
              ))}
            </select>
          </Explained>

          <Explained title="Destination server">
            <select
              aria-label="Destination server"
              value={allocation.server_id}
              onChange={(event) =>
                setAllocation({
                  ...allocation,
                  server_id: event.target.value,
                })
              }
            >
              <option value="">Destination server</option>
              {state.servers.map((server) => (
                <option key={server.id} value={server.id}>
                  {server.name}
                </option>
              ))}
            </select>
          </Explained>

          <Explained action title="Allocate VM">
            <button
              type="button"
              className="sim-button"
              disabled={busy || !allocation.vm_id || !allocation.server_id}
              onClick={() =>
                perform(
                  () => simulationApi.allocate(allocation),
                  "VM allocated successfully.",
                )
              }
            >
              <Plus size={16} />
              Allocate VM
            </button>
          </Explained>
        </section>

        <section className="sim-panel">
          <h3>Migrate VM</h3>
          <p>
            Move an assigned VM between servers. Capacity is checked before
            migration.
          </p>

          <Explained title="Destination server">
            <select
              aria-label="Destination server"
              value={migration.vm_id}
              onChange={(event) =>
                setMigration({
                  ...migration,
                  vm_id: event.target.value,
                  server_id: "",
                })
              }
            >
              <option value="">Select VM</option>
              {assignedVMs.map((vm) => (
                <option key={vm.id} value={vm.id}>
                  {vm.id} ({vm.server_id})
                </option>
              ))}
            </select>
          </Explained>

          <Explained title="Destination server">
            <select
              aria-label="Destination server"
              value={migration.server_id}
              onChange={(event) =>
                setMigration({
                  ...migration,
                  server_id: event.target.value,
                })
              }
            >
              <option value="">Destination server</option>

              {state.servers
                .filter((server) => {
                  const vm = assignedVMs.find(
                    (item) => item.id === migration.vm_id,
                  );
                  return server.id !== vm?.server_id;
                })
                .map((server) => (
                  <option key={server.id} value={server.id}>
                    {server.name}
                  </option>
                ))}
            </select>
          </Explained>

          <Explained action title="Migrate VM">
            <button
              type="button"
              className="sim-button"
              disabled={busy || !migration.vm_id || !migration.server_id}
              onClick={() =>
                perform(
                  () => simulationApi.migrate(migration),
                  "VM migration simulated successfully.",
                )
              }
            >
              <MoveRight size={16} />
              Migrate VM
            </button>
          </Explained>
        </section>

        <form className="sim-panel" onSubmit={addServer}>
          <h3>Add Physical Server</h3>

          <Explained title="Server ID">
            <input
              aria-label="Server ID"
              placeholder="Server ID (e.g. S4)"
              value={newServer.id}
              onChange={(event) =>
                setNewServer({
                  ...newServer,
                  id: event.target.value,
                })
              }
            />
          </Explained>

          <Explained title="Server name">
            <input
              aria-label="Server name"
              placeholder="Server name"
              value={newServer.name}
              onChange={(event) =>
                setNewServer({
                  ...newServer,
                  name: event.target.value,
                })
              }
            />
          </Explained>

          <label>CPU capacity (vCPU)</label>
          <Explained title="CPU capacity (vCPU)">
            <input
              aria-label="CPU capacity (vCPU)"
              type="number"
              min="0.1"
              step="any"
              value={newServer.cpu_capacity}
              onChange={(event) =>
                setNewServer({
                  ...newServer,
                  cpu_capacity: Number(event.target.value),
                })
              }
            />
          </Explained>

          <label>Memory capacity (GB)</label>
          <Explained title="Memory capacity (GB)">
            <input
              aria-label="Memory capacity (GB)"
              type="number"
              min="0.1"
              step="any"
              value={newServer.memory_capacity}
              onChange={(event) =>
                setNewServer({
                  ...newServer,
                  memory_capacity: Number(event.target.value),
                })
              }
            />
          </Explained>

          <Explained action title="Add Server">
            <button type="submit" className="sim-button" disabled={busy}>
              <Plus size={16} />
              Add Server
            </button>
          </Explained>
        </form>

        <form className="sim-panel" onSubmit={addVM}>
          <h3>Create Virtual Machine</h3>

          <Explained title="VM ID">
            <input
              aria-label="VM ID"
              placeholder="VM ID (e.g. VM7)"
              value={newVM.id}
              onChange={(event) =>
                setNewVM({
                  ...newVM,
                  id: event.target.value,
                })
              }
            />
          </Explained>

          <Explained title="VM name">
            <input
              aria-label="VM name"
              placeholder="VM name"
              value={newVM.name}
              onChange={(event) =>
                setNewVM({
                  ...newVM,
                  name: event.target.value,
                })
              }
            />
          </Explained>

          <label>Required vCPU</label>
          <Explained title="Required vCPU">
            <input
              aria-label="Required vCPU"
              type="number"
              min="0.1"
              step="any"
              value={newVM.cpu}
              onChange={(event) =>
                setNewVM({
                  ...newVM,
                  cpu: Number(event.target.value),
                })
              }
            />
          </Explained>

          <label>Required memory (GB)</label>
          <Explained title="Required memory (GB)">
            <input
              aria-label="Required memory (GB)"
              type="number"
              min="0.1"
              step="any"
              value={newVM.memory}
              onChange={(event) =>
                setNewVM({
                  ...newVM,
                  memory: Number(event.target.value),
                })
              }
            />
          </Explained>

          <Explained action title="Create VM">
            <button type="submit" className="sim-button" disabled={busy}>
              <Plus size={16} />
              Create VM
            </button>
          </Explained>
        </form>
      </div>

      <div className="sim-panel">
        <h3>Unassigned Virtual Machines</h3>

        {unassignedVMs.length === 0 ? (
          <p>All VMs are currently assigned.</p>
        ) : (
          unassignedVMs.map((vm) => (
            <div key={vm.id} className="sim-unassigned">
              <strong>
                {vm.id} — {vm.name}
              </strong>
              <span>
                {vm.cpu} vCPU · {vm.memory} GB RAM
              </span>
            </div>
          ))
        )}
      </div>
    </section>
  );
}
