@app.route('/dashboard')
def dashboard():
    if not session.get('user'):
        return redirect(url_for('signin'))
    
    # Gather live metrics from global objects (sensor, pump, history)
    level = sensor.water_level_l
    level_percent = round(level / config.TANK_CAPACITY_L * 100, 1)
    pump_running = pump.is_running
    energy_kwh = pump.total_energy_kwh
    water_m3 = pump.total_water_pumped_l / 1000.0
    energy_per_m3 = round(energy_kwh / water_m3, 2) if water_m3 > 0 else 0
    tariff = config.get_tariff_rate(time.localtime().tm_hour)
    cost_tzs = round(energy_kwh * tariff, 0)
    efficiency = round(pump.total_water_pumped_l / max(0.001, energy_kwh), 1)
    
    # Prepare table data from history
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
    
    # Get last decision reason from CSV log
    last_reason = "Waiting for data..."
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
