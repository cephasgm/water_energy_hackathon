# data_logger.py
import csv
import os
from config import DATA_LOG_FILE

class DataLogger:
    def __init__(self, filename=DATA_LOG_FILE):
        self.filename = filename
        self.fieldnames = ["timestamp", "water_level_l", "outflow_lps", "pressure_bar",
                           "pump_running", "energy_kwh_total", "decision_reason",
                           "tariff_rate", "leak_flag"]
        if not os.path.exists(filename):
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()

    def log(self, data_dict):
        with open(self.filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writerow(data_dict)
