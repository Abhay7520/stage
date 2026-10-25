from threading import Lock


class SimulationError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.status_code = status_code


class DataCenterSimulator:
    def __init__(self):
        self.lock = Lock()
        self.reset()

    def reset(self):
        with self.lock:
            self.servers = {
                "S1": {
                    "id": "S1",
                    "name": "Server 1",
                    "cpu_capacity": 16.0,
                    "memory_capacity": 32.0,
                },
                "S2": {
                    "id": "S2",
                    "name": "Server 2",
                    "cpu_capacity": 16.0,
                    "memory_capacity": 32.0,
                },
                "S3": {
                    "id": "S3",
                    "name": "Server 3",
                    "cpu_capacity": 8.0,
                    "memory_capacity": 16.0,
                },
            }

            self.vms = {
                "VM1": {
                    "id": "VM1",
                    "name": "Web Application",
                    "cpu": 4.0,
                    "memory": 8.0,
                    "server_id": "S1",
                },
                "VM2": {
                    "id": "VM2",
                    "name": "Database",
                    "cpu": 6.0,
                    "memory": 8.0,
                    "server_id": "S1",
                },
                "VM3": {
                    "id": "VM3",
                    "name": "Analytics",
                    "cpu": 4.0,
                    "memory": 8.0,
                    "server_id": "S2",
                },
                "VM4": {
                    "id": "VM4",
                    "name": "API Service",
                    "cpu": 3.0,
                    "memory": 6.0,
                    "server_id": "S2",
                },
                "VM5": {
                    "id": "VM5",
                    "name": "Background Worker",
                    "cpu": 2.0,
                    "memory": 4.0,
                    "server_id": "S3",
                },
                "VM6": {
                    "id": "VM6",
                    "name": "New Service",
                    "cpu": 2.0,
                    "memory": 4.0,
                    "server_id": None,
                },
            }

            return self._snapshot()

    def _usage(self, server_id):
        cpu = 0.0
        memory = 0.0

        for vm in self.vms.values():
            if vm["server_id"] == server_id:
                cpu += vm["cpu"]
                memory += vm["memory"]

        return cpu, memory

    def _snapshot(self):
        servers = []

        for server in self.servers.values():
            cpu_used, memory_used = self._usage(server["id"])

            cpu_percent = cpu_used / server["cpu_capacity"] * 100
            memory_percent = memory_used / server["memory_capacity"] * 100

            server_vms = [
                dict(vm) for vm in self.vms.values() if vm["server_id"] == server["id"]
            ]

            servers.append(
                {
                    **server,
                    "cpu_used": cpu_used,
                    "memory_used": memory_used,
                    "cpu_available": (server["cpu_capacity"] - cpu_used),
                    "memory_available": (server["memory_capacity"] - memory_used),
                    "cpu_percent": round(cpu_percent, 2),
                    "memory_percent": round(memory_percent, 2),
                    "status": (
                        "high" if max(cpu_percent, memory_percent) >= 85 else "normal"
                    ),
                    "vms": server_vms,
                }
            )

        unassigned = sum(vm["server_id"] is None for vm in self.vms.values())

        total_cpu = sum(server["cpu_capacity"] for server in self.servers.values())
        used_cpu = sum(server["cpu_used"] for server in servers)

        total_memory = sum(
            server["memory_capacity"] for server in self.servers.values()
        )
        used_memory = sum(server["memory_used"] for server in servers)

        metrics = {
            "total_servers": len(self.servers),
            "total_vms": len(self.vms),
            "assigned_vms": len(self.vms) - unassigned,
            "unassigned_vms": unassigned,
            "total_cpu": total_cpu,
            "used_cpu": used_cpu,
            "total_memory": total_memory,
            "used_memory": used_memory,
            "cpu_utilization_percent": (
                round(used_cpu / total_cpu * 100, 2) if total_cpu else 0.0
            ),
            "memory_utilization_percent": (
                round(used_memory / total_memory * 100, 2) if total_memory else 0.0
            ),
            "high_utilization_servers": sum(
                server["status"] == "high" for server in servers
            ),
        }

        return {
            "servers": servers,
            "vms": [dict(vm) for vm in self.vms.values()],
            "metrics": metrics,
        }

    def get_state(self):
        with self.lock:
            return self._snapshot()

    def get_metrics(self):
        with self.lock:
            return self._snapshot()["metrics"]

    def create_server(self, server_id, name, cpu_capacity, memory_capacity):
        with self.lock:
            if server_id in self.servers:
                raise SimulationError("Server ID already exists.", 409)

            if cpu_capacity <= 0 or memory_capacity <= 0:
                raise SimulationError("Server capacities must be positive.")

            self.servers[server_id] = {
                "id": server_id,
                "name": name,
                "cpu_capacity": float(cpu_capacity),
                "memory_capacity": float(memory_capacity),
            }

            return self._snapshot()

    def create_vm(self, vm_id, name, cpu, memory):
        with self.lock:
            if vm_id in self.vms:
                raise SimulationError("VM ID already exists.", 409)

            if cpu <= 0 or memory <= 0:
                raise SimulationError("VM resources must be positive.")

            self.vms[vm_id] = {
                "id": vm_id,
                "name": name,
                "cpu": float(cpu),
                "memory": float(memory),
                "server_id": None,
            }

            return self._snapshot()

    def _validate_destination(self, vm, server_id):
        if server_id not in self.servers:
            raise SimulationError("Destination server not found.", 404)

        server = self.servers[server_id]
        used_cpu, used_memory = self._usage(server_id)

        if used_cpu + vm["cpu"] > server["cpu_capacity"] + 1e-9:
            raise SimulationError("Insufficient CPU capacity.", 409)

        if used_memory + vm["memory"] > server["memory_capacity"] + 1e-9:
            raise SimulationError("Insufficient memory capacity.", 409)

    def allocate_vm(self, vm_id, server_id):
        with self.lock:
            if vm_id not in self.vms:
                raise SimulationError("VM not found.", 404)

            vm = self.vms[vm_id]

            if vm["server_id"] is not None:
                raise SimulationError(
                    "VM is already assigned. " "Use migration instead.", 409
                )

            self._validate_destination(vm, server_id)

            vm["server_id"] = server_id
            return self._snapshot()

    def migrate_vm(self, vm_id, server_id):
        with self.lock:
            if vm_id not in self.vms:
                raise SimulationError("VM not found.", 404)

            vm = self.vms[vm_id]

            if vm["server_id"] is None:
                raise SimulationError(
                    "VM is unassigned. " "Use allocation instead.", 409
                )

            if vm["server_id"] == server_id:
                raise SimulationError("VM is already on this server.", 409)

            # Validate before changing the source
            # placement. Failed migrations leave the
            # original placement unchanged.
            self._validate_destination(vm, server_id)

            vm["server_id"] = server_id
            return self._snapshot()
