# sensor_simulator.py
import random
import time
import numpy as np
from config import TANK_CAPACITY_L, MIN_LEVEL_L

class SensorSimulator:
    def __init__(self, initial_level=3000.0):
        self.water_level_l = initial_level
        self.water_outflow_l_per_sec = 0.2   # base consumption (0.2 L/s = 720 L/h)
        self.noise_std = 0.05
        self.leak_active = False              # can be toggled for anomaly detection

    def update(self):
        """Simulate one second of water usage and random variations."""
        # Human consumption pattern (sinusoidal daily cycle)
        t = time.time() % 86400
        hour = (t / 3600) % 24
        # Morning (6–9) and evening (18–21) peaks
        demand_factor = 1.0 + 0.8 * np.sin((hour - 6) / 12 * np.pi)
        base_outflow = self.water_outflow_l_per_sec * demand_factor

        # Add random noise
        outflow = max(0.05, base_outflow + np.random.normal(0, 0.05))

        # Leak simulation (if enabled)
        if self.leak_active:
            outflow += 0.3   # extra 0.3 L/s leak

        # Update water level (will be decreased by pump controller when pump runs)
        self.water_level_l -= outflow
        self.water_level_l = max(0.0, min(TANK_CAPACITY_L, self.water_level_l))

        # Simulate sensor noise
        measured_level = self.water_level_l + np.random.normal(0, self.noise_std * self.water_level_l)
        measured_level = max(0.0, measured_level)

        return {
            "timestamp": time.time(),
            "water_level_l": round(measured_level, 1),
            "outflow_l_per_sec": round(outflow, 2),
            "pressure_bar": round(measured_level / TANK_CAPACITY_L * 3.0, 2),  # 3 bar at full
            "leak_detected": self.leak_active and outflow > 0.5
        }

    def set_leak(self, status):
        self.leak_active = status
