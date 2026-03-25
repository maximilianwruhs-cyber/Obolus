import os
import subprocess
import time
import json
import psutil
import requests

import config


class HardwareSensorium:
    """
    Hardware Feedback Loop.
    Reads real hardware metrics to influence the efficiency factor (eta).
    """

    def __init__(self, state_file=None):
        self.state_file = state_file or str(config.DATA_DIR / "hardware_state.json")
        self.cached_price = None
        self.price_timestamp = 0

    def get_cpu_temp(self):
        try:
            temps = []
            for i in range(10):
                path = f"/sys/class/thermal/thermal_zone{i}/temp"
                if os.path.exists(path):
                    with open(path, "r") as f:
                        temps.append(int(f.read().strip()) / 1000.0)
            return max(temps) if temps else 40.0
        except Exception:
            return 45.0

    def get_system_load(self):
        try:
            with open("/proc/loadavg", "r") as f:
                return float(f.read().split()[0])
        except Exception:
            return 1.0

    def get_io_wait(self):
        try:
            output = subprocess.check_output(
                ["iostat", "-c"], stderr=subprocess.STDOUT
            ).decode()
            lines = output.splitlines()
            for i, line in enumerate(lines):
                if "avg-cpu:" in line:
                    metrics = lines[i + 1].split()
                    return float(metrics[3])
            return 0.0
        except Exception:
            return 0.5

    def get_battery_state(self):
        try:
            capacities = []
            for i in range(5):
                path = f"/sys/class/power_supply/BAT{i}/capacity"
                if os.path.exists(path):
                    with open(path, "r") as f:
                        capacities.append(int(f.read().strip()))

            status_path = "/sys/class/power_supply/BAT0/status"
            if not os.path.exists(status_path):
                status_path = "/sys/class/power_supply/BAT1/status"

            if os.path.exists(status_path):
                with open(status_path, "r") as f:
                    status = f.read().strip()
            else:
                status = "Unknown"

            avg_cap = sum(capacities) / len(capacities) if capacities else 100
            return avg_cap, status
        except Exception:
            return 100, "Unknown"

    def get_live_energy_price_c_kwh(self) -> float:
        """Fetches current hourly electricity spot price from AWattar API (Cent/kWh)."""
        now = time.time()
        if self.cached_price is not None and (now - self.price_timestamp) < 300:
            return self.cached_price

        try:
            resp = requests.get("https://api.awattar.at/v1/marketdata", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("data") and len(data["data"]) > 0:
                    eur_mwh = data["data"][0]["marketprice"]
                    c_kwh = eur_mwh / 10.0
                    self.cached_price = round(c_kwh, 2)
                    self.price_timestamp = now
                    return self.cached_price
        except Exception:
            pass
        return 15.0  # Fallback: Austrian average ~15c/kWh

    def capture_metrics(self):
        bat_cap, bat_status = self.get_battery_state()
        market_c_kwh = self.get_live_energy_price_c_kwh()

        metrics = {
            "timestamp": time.time(),
            "cpu_temp": self.get_cpu_temp(),
            "load_1m": self.get_system_load(),
            "io_wait": self.get_io_wait(),
            "battery_capacity": bat_cap,
            "battery_status": bat_status,
            "thermal_throttle": 1.0 if self.get_cpu_temp() < 75.0 else 0.5,
            "market_price_c_kwh": market_c_kwh,
        }

        bat_penalty = 0.0
        if bat_cap < 20 and bat_status != "Charging":
            bat_penalty = (20 - bat_cap) * 0.05

        temp_penalty = max(0, (metrics["cpu_temp"] - 50) * 0.02)
        load_penalty = max(0, (metrics["load_1m"] - 4.0) * 0.1)

        econ_multiplier = 1.0
        if market_c_kwh < 0:
            econ_multiplier = 0.5
        elif market_c_kwh < 5.0:
            econ_multiplier = 0.8
        elif market_c_kwh > 20.0:
            econ_multiplier = 1.5

        total_penalty = (temp_penalty + load_penalty + bat_penalty) * econ_multiplier

        base_h = 1.0 - total_penalty
        if market_c_kwh < 0:
            base_h += 0.2

        metrics["hardware_efficiency_factor"] = round(max(0.01, base_h), 3)

        with open(self.state_file, "w") as f:
            json.dump(metrics, f, indent=4)

        return metrics


if __name__ == "__main__":
    sensor = HardwareSensorium()
    data = sensor.capture_metrics()
    print(
        f"[SENSORIUM] Metrics: Temp={data['cpu_temp']}°C, "
        f"Load={data['load_1m']}, H-Factor={data['hardware_efficiency_factor']}"
    )
