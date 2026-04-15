import time
from config import MIN_LEVEL_L, MAX_LEVEL_L, get_tariff_rate

class OptimizationEngine:
    def __init__(self, lookahead_minutes=30):
        self.lookahead = lookahead_minutes
        self.last_decision = None

    def should_start_pump(self, water_level, current_hour, forecast_demand=None):
        if water_level < MIN_LEVEL_L * 1.2:
            return True, "Emergency: low water level"
        if water_level > MAX_LEVEL_L:
            return False, "Tank near full"
        tariff = get_tariff_rate(current_hour)
        if tariff < 300 and water_level < (MAX_LEVEL_L * 0.8):
            return True, f"Off-peak tariff ({tariff} TZS/kWh)"
        if forecast_demand and forecast_demand > 0.5:
            if water_level < (MAX_LEVEL_L * 0.7):
                return True, "High demand forecast"
        return False, "Tariff not favourable / level sufficient"

    def predict_demand(self, historical_outflows):
        if len(historical_outflows) < 10:
            return 0.3
        return sum(historical_outflows[-30:]) / min(30, len(historical_outflows))

