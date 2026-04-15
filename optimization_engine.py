# optimization_engine.py
import time
from config import MIN_LEVEL_L, MAX_LEVEL_L, get_tariff_rate

class OptimizationEngine:
    def __init__(self, lookahead_minutes=30):
        self.lookahead = lookahead_minutes
        self.last_decision = None

    def should_start_pump(self, water_level, current_hour, forecast_demand=None):
        """
        Returns (decision, reason)
        decision: True = start pump, False = keep off
        """
        # Emergency: water too low
        if water_level < MIN_LEVEL_L * 1.2:   # below 1200 L
            return True, "Emergency: low water level"

        # Do not overfill
        if water_level > MAX_LEVEL_L:
            return False, "Tank near full"

        # Time‑of‑use optimisation
        tariff = get_tariff_rate(current_hour)
        # Simple rule: start pump if tariff is off_peak and level not too high
        if tariff < 300 and water_level < (MAX_LEVEL_L * 0.8):
            return True, f"Off‑peak tariff ({tariff} TZS/kWh)"

        # If forecast demand high, pre‑fill
        if forecast_demand and forecast_demand > 0.5:   # high demand predicted
            if water_level < (MAX_LEVEL_L * 0.7):
                return True, "High demand forecast"

        # Default: wait
        return False, "Tariff not favourable / level sufficient"

    def predict_demand(self, historical_outflows):
        """Simple moving average forecast (30 sec window)."""
        if len(historical_outflows) < 10:
            return 0.3
        return sum(historical_outflows[-30:]) / min(30, len(historical_outflows))
