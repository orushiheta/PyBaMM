#
# Test setting up a simulation with an experiment
#
import pybamm
import unittest


class TestSimulationExperiment(unittest.TestCase):
    def test_set_up(self):
        experiment = pybamm.Experiment(
            [
                "Discharge at C/20 for 1 hour",
                "Charge at 1 A until 4.1 V",
                "Hold at 4.1 V until 50 mA",
                "Discharge at 2 W for 1 hour",
            ],
        )
        model = pybamm.lithium_ion.DFN()
        sim = pybamm.Simulation(model, experiment=experiment)

        self.assertEqual(sim.experiment, experiment)
        self.assertEqual(
            sim._experiment_inputs[0]["Current input [A]"],
            1 / 20 * model.default_parameter_values["Cell capacity [A.h]"],
        )
        self.assertEqual(sim._experiment_inputs[0]["Current switch"], 1)
        self.assertEqual(sim._experiment_inputs[0]["Voltage switch"], 0)
        self.assertEqual(sim._experiment_inputs[0]["Power switch"], 0)
        self.assertEqual(sim._experiment_inputs[0]["Current cut-off [A]"], -1e10)
        self.assertEqual(sim._experiment_inputs[0]["Voltage cut-off [V]"], -1e10)
        self.assertEqual(sim._experiment_inputs[1]["Current input [A]"], -1)
        self.assertEqual(sim._experiment_inputs[1]["Current switch"], 1)
        self.assertEqual(sim._experiment_inputs[1]["Voltage switch"], 0)
        self.assertEqual(sim._experiment_inputs[1]["Power switch"], 0)
        self.assertEqual(sim._experiment_inputs[1]["Current cut-off [A]"], -1e10)
        self.assertEqual(sim._experiment_inputs[1]["Voltage cut-off [V]"], 4.1)
        self.assertEqual(sim._experiment_inputs[2]["Current switch"], 0)
        self.assertEqual(sim._experiment_inputs[2]["Voltage switch"], 1)
        self.assertEqual(sim._experiment_inputs[2]["Power switch"], 0)
        self.assertEqual(sim._experiment_inputs[2]["Voltage input [V]"], 4.1)
        self.assertEqual(sim._experiment_inputs[2]["Current cut-off [A]"], 0.05)
        self.assertEqual(sim._experiment_inputs[2]["Voltage cut-off [V]"], -1e10)
        self.assertEqual(sim._experiment_inputs[3]["Current switch"], 0)
        self.assertEqual(sim._experiment_inputs[3]["Voltage switch"], 0)
        self.assertEqual(sim._experiment_inputs[3]["Power switch"], 1)
        self.assertEqual(sim._experiment_inputs[3]["Power input [W]"], 2)
        self.assertEqual(sim._experiment_inputs[3]["Current cut-off [A]"], -1e10)
        self.assertEqual(sim._experiment_inputs[3]["Voltage cut-off [V]"], -1e10)

        tau = sim._parameter_values.evaluate(model.timescale)
        self.assertEqual(
            sim._experiment_times,
            [t / tau for t in [3600, 7 * 24 * 3600, 7 * 24 * 3600, 3600]],
        )

        self.assertIn("Current cut-off (positive) [A] [experiment]", sim.model.events)
        self.assertIn("Current cut-off (negative) [A] [experiment]", sim.model.events)
        self.assertIn("Voltage cut-off [V] [experiment]", sim.model.events)

    def test_run_experiment(self):
        experiment = pybamm.Experiment(
            [
                "Discharge at C/20 for 1 hour",
                "Charge at 1 A until 4.1 V",
                "Hold at 4.1 V until 50 mA",
                "Discharge at 2 W for 1 hour",
            ],
        )
        model = pybamm.lithium_ion.SPM()
        sim = pybamm.Simulation(model, experiment=experiment)
        sim.solve()
        self.assertEqual(sim._solution.termination, "final time")

    def test_run_experiment_breaks_early(self):
        experiment = pybamm.Experiment(["Discharge at 2 C for 1 hour"])
        model = pybamm.lithium_ion.SPM()
        sim = pybamm.Simulation(model, experiment=experiment)
        pybamm.set_logging_level("ERROR")
        sim.solve()
        pybamm.set_logging_level("WARNING")
        self.assertEqual(sim._solution.termination, "event: Minimum voltage")


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    pybamm.settings.debug_mode = True
    unittest.main()
