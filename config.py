# config.py
import json
from datetime import time

# Tank parameters
TANK_CAPACITY_L = 5000.0          # litres
MIN_LEVEL_L = 1000.0              # reserve water
MAX_LEVEL_L = 4500.0              # safety margin
PUMP_FLOW_RATE_L_PER_SEC = 2.0    # 2 L/s = 7.2 m³/h
PUMP_POWER_KW = 2.2               # 2.2 kW pump

# Time‑of‑Use electricity tariff (TZS per kWh)
TARIFF = {
    "peak": 450.0,      # 6:00–10:00, 18:00–22:00
    "off_peak": 280.0,  # 22:00–6:00
    "shoulder": 350.0   # 10:00–18:00
}

def get_tariff_rate(hour):
    if (6 <= hour < 10) or (18 <= hour < 22):
        return TARIFF["peak"]
    elif (22 <= hour) or (hour < 6):
        return TARIFF["off_peak"]
    else:
        return TARIFF["shoulder"]

# Simulation settings
SIMULATION_STEP_SEC = 1            # 1 second = 1 second simulated time
SIMULATION_DURATION_SEC = 3600     # run 1 hour of simulated time (can be changed)
DATA_LOG_FILE = "water_energy_log.csv"

# Control hysteresis
PUMP_MIN_RUN_SEC = 30              # avoid short cycling
PUMP_COOLDOWN_SEC = 10
