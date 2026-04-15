# test_all.py
import unittest
import time
from sensor_simulator import SensorSimulator
from optimization_engine import OptimizationEngine
from pump_controller import PumpController
from config import get_tariff_rate, MIN_LEVEL_L, MAX_LEVEL_L

class TestWaterEnergySystem(unittest.TestCase):

    def test_sensor_update(self):
        sens = SensorSimulator(initial_level=2000)
        data = sens.update()
        self.assertIn("water_level_l", data)
        self.assertGreaterEqual(data["water_level_l"], 0)
        self.assertLessEqual(data["water_level_l"], 5000)

    def test_tariff_hours(self):
        self.assertEqual(get_tariff_rate(3), 280)   # off_peak
        self.assertEqual(get_tariff_rate(8), 450)   # peak
        self.assertEqual(get_tariff_rate(14), 350)  # shoulder

    def test_optimizer_emergency(self):
        opt = OptimizationEngine()
        decision, reason = opt.should_start_pump(500, 14)  # very low level
        self.assertTrue(decision)
        self.assertIn("low water", reason)

    def test_optimizer_offpeak(self):
        opt = OptimizationEngine()
        decision, reason = opt.should_start_pump(3000, 3)  # off-peak hour 3 AM
        self.assertTrue(decision)
        self.assertIn("Off‑peak", reason)

    def test_pump_min_run(self):
        pump = PumpController()
        # Start pump
        new_level, _ = pump.update(2000, True, time.time())
        self.assertTrue(pump.is_running)
        # Try to stop immediately – should be ignored because min run not met
        new_level2, _ = pump.update(2100, False, time.time() + 5)
        self.assertTrue(pump.is_running)   # still running
        # After min run + cooldown
        new_level3, _ = pump.update(2200, False, time.time() + 40)
        self.assertFalse(pump.is_running)

    def test_energy_accounting(self):
        pump = PumpController()
        # Run pump for 10 simulated seconds
        start_time = time.time()
        for _ in range(10):
            pump.update(3000, True, start_time)
            start_time += 1
        metrics = pump.get_metrics()
        self.assertAlmostEqual(metrics["total_energy_kwh"], (2.2 / 3600) * 10, places=4)
        self.assertAlmostEqual(metrics["total_water_pumped_m3"], (2.0 * 10) / 1000.0, places=2)

if __name__ == '__main__':
    unittest.main()
