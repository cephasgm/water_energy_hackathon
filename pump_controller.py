# pump_controller.py
import time
from config import PUMP_FLOW_RATE_L_PER_SEC, PUMP_POWER_KW, PUMP_MIN_RUN_SEC, PUMP_COOLDOWN_SEC

class PumpController:
    def __init__(self):
        self.is_running = False
        self.run_start_time = None
        self.total_energy_kwh = 0.0
        self.total_water_pumped_l = 0.0
        self.cooldown_until = 0

    def update(self, water_level, decision, current_time):
        """
        Apply pump control logic with hysteresis and min run time.
        Returns new water level after 1 second of pumping (if applicable).
        """
        if self.cooldown_until > current_time:
            # Pump is cooling down – cannot start
            return water_level, 0.0

        # Decide to start or stop
        if decision and not self.is_running:
            # Start pump if cooldown finished
            self.is_running = True
            self.run_start_time = current_time
        elif not decision and self.is_running:
            # Stop pump only if minimum run time satisfied
            if current_time - self.run_start_time >= PUMP_MIN_RUN_SEC:
                self.is_running = False
                self.cooldown_until = current_time + PUMP_COOLDOWN_SEC
            # else keep running until min run is met

        # Apply pumping effect
        if self.is_running:
            pumped = PUMP_FLOW_RATE_L_PER_SEC
            new_level = water_level + pumped
            # Energy consumed in this second
            energy_this_sec = PUMP_POWER_KW / 3600.0   # kWh per second
            self.total_energy_kwh += energy_this_sec
            self.total_water_pumped_l += pumped
            return new_level, pumped
        else:
            return water_level, 0.0

    def get_metrics(self):
        return {
            "pump_running": self.is_running,
            "total_energy_kwh": round(self.total_energy_kwh, 3),
            "total_water_pumped_m3": round(self.total_water_pumped_l / 1000.0, 2)
        }
