import json
from datetime import time

TANK_CAPACITY_L = 5000.0
MIN_LEVEL_L = 1000.0
MAX_LEVEL_L = 4500.0
PUMP_FLOW_RATE_L_PER_SEC = 2.0
PUMP_POWER_KW = 2.2

TARIFF = {
    "peak": 450.0,
    "off_peak": 280.0,
    "shoulder": 350.0
}

def get_tariff_rate(hour):
    if (6 <= hour < 10) or (18 <= hour < 22):
        return TARIFF["peak"]
    elif (22 <= hour) or (hour < 6):
        return TARIFF["off_peak"]
    else:
        return TARIFF["shoulder"]

SIMULATION_STEP_SEC = 1
SIMULATION_DURATION_SEC = 3600
DATA_LOG_FILE = "water_energy_log.csv"

PUMP_MIN_RUN_SEC = 30
PUMP_COOLDOWN_SEC = 10
