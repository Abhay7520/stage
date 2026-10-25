import unittest

from src.datacenter_simulator import (
    DataCenterSimulator,
    SimulationError,
)


class TestDataCenterSimulator(unittest.TestCase):

    def setUp(self):
        self.simulator = DataCenterSimulator()

    def test_initial_environment(self):
        state = self.simulator.get_state()

        self.assertEqual(state["metrics"]["total_servers"], 3)
        self.assertEqual(state["metrics"]["total_vms"], 6)
        self.assertEqual(state["metrics"]["unassigned_vms"], 1)

    def test_allocate_vm(self):
        state = self.simulator.allocate_vm("VM6", "S3")

        vm = next(vm for vm in state["vms"] if vm["id"] == "VM6")

        self.assertEqual(vm["server_id"], "S3")

    def test_migrate_vm(self):
        state = self.simulator.migrate_vm("VM1", "S2")

        vm = next(vm for vm in state["vms"] if vm["id"] == "VM1")

        self.assertEqual(vm["server_id"], "S2")

    def test_reject_cpu_overallocation(self):
        self.simulator.create_vm("VM_BIG", "Large VM", 10, 2)

        with self.assertRaises(SimulationError):
            self.simulator.allocate_vm("VM_BIG", "S1")

        vm = self.simulator.vms["VM_BIG"]
        self.assertIsNone(vm["server_id"])

    def test_reject_memory_overallocation(self):
        self.simulator.create_vm("VM_RAM", "Memory Heavy VM", 1, 30)

        with self.assertRaises(SimulationError):
            self.simulator.allocate_vm("VM_RAM", "S1")

        self.assertIsNone(self.simulator.vms["VM_RAM"]["server_id"])

    def test_failed_migration_is_atomic(self):
        self.simulator.create_server("S4", "Small Server", 1, 2)

        with self.assertRaises(SimulationError):
            self.simulator.migrate_vm("VM1", "S4")

        self.assertEqual(self.simulator.vms["VM1"]["server_id"], "S1")

    def test_duplicate_server_rejected(self):
        with self.assertRaises(SimulationError):
            self.simulator.create_server("S1", "Duplicate", 16, 32)

    def test_reset(self):
        self.simulator.allocate_vm("VM6", "S3")

        state = self.simulator.reset()

        self.assertEqual(state["metrics"]["unassigned_vms"], 1)


if __name__ == "__main__":
    unittest.main()
