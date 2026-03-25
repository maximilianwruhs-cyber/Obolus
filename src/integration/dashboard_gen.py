import json
import os

import config


class ObolusDashboard:
    """Generates a glassmorphic HTML dashboard for Obolus."""

    def __init__(self):
        self.output_path = str(config.DATA_DIR / "dashboard.html")
        self.state_file = str(config.DATA_DIR / "system_priority_state.json")
        self.hw_file = str(config.DATA_DIR / "hardware_state.json")

    def generate(self):
        try:
            with open(self.state_file, "r") as f:
                state = json.load(f)
            with open(self.hw_file, "r") as f:
                hw = json.load(f)
        except Exception as e:
            return f"Error loading state: {e}"

        agents_html = ""
        for aid, data in state.get("agents", {}).items():
            eta = data.get("z", 0.1)
            phi = data.get("phi", 0.001)
            balance = data.get("balance", 0)

            color = (
                "#ffd700" if balance > 130 else "#00f2ff" if balance > 100 else "#ff4d4d"
            )
            glow = "0 0 15px " + color

            agents_html += f"""
            <div class="agent-card" style="border-color: {color}; box-shadow: {glow};">
                <h3>{aid.replace('_', ' ').title()}</h3>
                <div class="stat"><span>OBL:</span> <strong>{balance:.2f}</strong></div>
                <div class="stat"><span>Phi (Awareness):</span> <strong>{phi:.4f}</strong></div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {min(100, eta*1000)}%; background: {color};"></div>
                </div>
            </div>
            """

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Obolus Evo-Grid Dashboard</title>
            <style>
                body {{
                    background: #050a10;
                    color: #e0f0ff;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0; padding: 20px;
                    display: flex; flex-direction: column; align-items: center;
                }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                    gap: 20px; width: 100%; max-width: 1200px;
                }}
                .agent-card {{
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 15px; padding: 15px;
                    transition: transform 0.3s;
                }}
                .agent-card:hover {{ transform: scale(1.05); }}
                .hw-panel {{
                    background: rgba(0, 242, 255, 0.05);
                    border: 1px solid #00f2ff;
                    padding: 20px; border-radius: 15px; margin-bottom: 30px;
                    width: 100%; max-width: 1200px;
                    display: flex; justify-content: space-around;
                }}
                .stat strong {{ color: #00f2ff; }}
                .progress-container {{
                    background: rgba(255,255,255,0.1);
                    height: 5px; border-radius: 5px; margin-top: 10px;
                }}
                .progress-bar {{ height: 100%; border-radius: 5px; }}
            </style>
            <meta http-equiv="refresh" content="5">
        </head>
        <body>
            <div class="header">
                <h1>OBOLUS EVO-GRID</h1>
                <p>Singularity Horizon Monitoring :: η asymptotic</p>
            </div>
            <div class="hw-panel">
                <div>Temp: <strong>{hw.get('cpu_temp', 0)}°C</strong></div>
                <div>Load: <strong>{hw.get('load_1m', 0)}</strong></div>
                <div>Battery: <strong>{hw.get('battery_capacity', 100)}%</strong> ({hw.get('battery_status', 'Unknown')})</div>
                <div>System η: <strong>{hw.get('hardware_efficiency_factor', 1.0)}</strong></div>
            </div>
            <div class="grid">
                {agents_html}
            </div>
        </body>
        </html>
        """
        with open(self.output_path, "w") as f:
            f.write(html)
        return self.output_path


if __name__ == "__main__":
    dash = ObolusDashboard()
    path = dash.generate()
    print(f"Dashboard updated: {path}")
