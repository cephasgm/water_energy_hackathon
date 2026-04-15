# app.py - Complete working version for Water-Energy Hackathon 2026

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import threading
import time
import hashlib
from sensor_simulator import SensorSimulator
from optimization_engine import OptimizationEngine
from pump_controller import PumpController
from data_logger import DataLogger
import config

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'hackathon2026_secret_key_change_in_production'

# Global state
sensor = SensorSimulator(initial_level=3000.0)
optimizer = OptimizationEngine()
pump = PumpController()
logger = DataLogger()

history = {
    "timestamps": [], "water_level": [], "pump_state": [],
    "energy_kwh": [], "tariff": []
}
simulation_running = True
last_outflows = []

# Mock user database (in memory)
users = {}  # email -> {name, password_hash}

def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

# Simulation loop
def simulation_loop():
    global simulation_running, last_outflows
    while simulation_running:
        loop_start = time.time()
        sensor_data = sensor.update()
        water_level = sensor_data["water_level_l"]
        outflow = sensor_data["outflow_l_per_sec"]
        last_outflows.append(outflow)
        if len(last_outflows) > 300:
            last_outflows.pop(0)
        current_hour = time.localtime().tm_hour
        tariff = config.get_tariff_rate(current_hour)
        forecast = optimizer.predict_demand(last_outflows)
        decision, reason = optimizer.should_start_pump(water_level, current_hour, forecast)
        new_level, pumped = pump.update(water_level, decision, time.time())
        sensor.water_level_l = new_level
        energy_kwh = pump.total_energy_kwh
        log_entry = {
            "timestamp": time.time(),
            "water_level_l": round(new_level, 1),
            "outflow_lps": round(outflow, 2),
            "pressure_bar": sensor_data["pressure_bar"],
            "pump_running": pump.is_running,
            "energy_kwh_total": round(energy_kwh, 3),
            "decision_reason": reason,
            "tariff_rate": tariff,
            "leak_flag": sensor_data["leak_detected"]
        }
        logger.log(log_entry)
        history["timestamps"].append(time.time())
        history["water_level"].append(new_level)
        history["pump_state"].append(1 if pump.is_running else 0)
        history["energy_kwh"].append(energy_kwh)
        history["tariff"].append(tariff)
        for key in history:
            if len(history[key]) > 200:
                history[key].pop(0)
        elapsed = time.time() - loop_start
        time.sleep(max(0, config.SIMULATION_STEP_SEC - elapsed))

# Start simulation thread
threading.Thread(target=simulation_loop, daemon=True).start()

# ------------------- ROUTES -------------------
@app.route('/')
def landing():
    return render_template('index.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('user'):
        return redirect(url_for('signin'))
    
    level = sensor.water_level_l
    level_percent = round(level / config.TANK_CAPACITY_L * 100, 1)
    pump_running = pump.is_running
    energy_kwh = pump.total_energy_kwh
    water_m3 = pump.total_water_pumped_l / 1000.0
    energy_per_m3 = round(energy_kwh / water_m3, 2) if water_m3 > 0 else 0
    tariff = config.get_tariff_rate(time.localtime().tm_hour)
    cost_tzs = round(energy_kwh * tariff, 0)
    efficiency = round(pump.total_water_pumped_l / max(0.001, energy_kwh), 1)
    
    # Prepare table data
    table_data = []
    if history["timestamps"]:
        now = time.time()
        for i in range(min(15, len(history["timestamps"]))):
            idx = -i-1
            table_data.insert(0, {
                "time_ago": round(now - history["timestamps"][idx], 1),
                "level": history["water_level"][idx],
                "pump": history["pump_state"][idx],
                "energy": history["energy_kwh"][idx],
                "tariff": history["tariff"][idx]
            })
    
    # Get last decision reason
    last_reason = "Optimisation active"
    try:
        with open(config.DATA_LOG_FILE, 'r') as f:
            lines = f.readlines()
            if len(lines) > 1:
                last_reason = lines[-1].split(',')[5]
    except:
        pass
    
    return render_template('dashboard.html',
                           level=round(level,1),
                           level_percent=level_percent,
                           pump_running=pump_running,
                           energy_kwh=round(energy_kwh,2),
                           water_m3=round(water_m3,2),
                           energy_per_m3=energy_per_m3,
                           cost_tzs=cost_tzs,
                           decision_reason=last_reason,
                           leak=sensor.leak_active,
                           efficiency=efficiency,
                           table_data=table_data)

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if email in users and users[email]['password_hash'] == hash_password(password):
        session['user'] = email
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.json
    email = data.get('email')
    if email in users:
        return jsonify({'success': False, 'message': 'Email already exists'})
    users[email] = {
        'name': data.get('name'),
        'password_hash': hash_password(data.get('password'))
    }
    return jsonify({'success': True})

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('landing'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)