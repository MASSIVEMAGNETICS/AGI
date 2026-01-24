
```python
#!/usr/bin/env python3
import asyncio
import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Dict, Any
import logging
from pulse_fractal_mesh import PulseTelemetryBus, FractalMeshOrchestrator, SensorHub, SystemWatchdog, MQTTPublisher, CONFIG

class FractalMeshGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fractal Mesh Network Control Panel")
        self.geometry("800x600")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Initialize core components
        self.bus = PulseTelemetryBus(history=CONFIG["MAX_HISTORY"])
        self.watchdog = SystemWatchdog(self.bus)
        self.mqtt_pub = MQTTPublisher(self.bus)
        self.mesh = FractalMeshOrchestrator(self.bus, brain_device="cpu", watchdog=self.watchdog)
        self.sensor = SensorHub(self.bus, name="OmniSense", beat_s=CONFIG["HEARTBEAT_INTERVAL_S"], snapshot_minutes=CONFIG["SNAPSHOT_INTERVAL_MINUTES"])

        # Subscribe to bus for GUI updates
        self.bus.subscribe(self.update_gui)

        # GUI Layout
        self.create_widgets()

        # Start sensor hub
        asyncio.create_task(self.sensor.start())

    def create_widgets(self):
        # Sensor Data Display
        self.sensor_frame = ttk.LabelFrame(self, text="Sensor Data")
        self.sensor_frame.pack(fill="x", padx=5, pady=5)
        self.sensor_text = scrolledtext.ScrolledText(self.sensor_frame, height=5, width=80)
        self.sensor_text.pack(padx=5, pady=5)

        # Mesh Activity Display
        self.mesh_frame = ttk.LabelFrame(self, text="Mesh Activity")
        self.mesh_frame.pack(fill="x", padx=5, pady=5)
        self.mesh_text = scrolledtext.ScrolledText(self.mesh_frame, height=5, width=80)
        self.mesh_text.pack(padx=5, pady=5)

        # System Health Display
        self.health_frame = ttk.LabelFrame(self, text="System Health")
        self.health_frame.pack(fill="x", padx=5, pady=5)
        self.health_text = scrolledtext.ScrolledText(self.health_frame, height=5, width=80)
        self.health_text.pack(padx=5, pady=5)

        # Pulse Injection
        self.inject_frame = ttk.LabelFrame(self, text="Inject Pulse")
        self.inject_frame.pack(fill="x", padx=5, pady=5)
        self.inject_entry = ttk.Entry(self.inject_frame, width=50)
        self.inject_entry.pack(side="left", padx=5, pady=5)
        self.inject_button = ttk.Button(self.inject_frame, text="Inject", command=self.inject_pulse)
        self.inject_button.pack(side="left", padx=5, pady=5)

    async def update_gui(self, pulse: Dict[str, Any]):
        # Update sensor data
        if pulse["type"] == "sensor.beat":
            self.sensor_text.delete(1.0, tk.END)
            payload = pulse["payload"]
            self.sensor_text.insert(tk.END, f"Temp: {payload['tempC']}°C, "
                                          f"Humidity: {payload['humidity']}%, "
                                          f"Pressure: {payload['pressure_hPa']}hPa, "
                                          f"Light: {payload['light']}, "
                                          f"Voltage: {payload['voltage_V']}V\n"
                                          f"CPU: {payload['cpu_percent']}%, "
                                          f"Memory: {payload['memory_percent']}%, "
                                          f"Disk: {payload['disk_percent']}%")

        # Update mesh activity
        if pulse["type"] == "node.think":
            self.mesh_text.delete(1.0, tk.END)
            payload = pulse["payload"]
            self.mesh_text.insert(tk.END, f"Node: {payload['node']}, "
                                        f"Pulse ID: {payload['pulse_id']}, "
                                        f"Hop: {payload['hop']}, "
                                        f"Alignment: {payload['alignment']:.2f}, "
                                        f"Complexity: {payload['complexity']:.2f}, "
                                        f"Path: {payload['path']}")

        # Update system health
        if pulse["type"] == "system.watchdog":
            self.health_text.delete(1.0, tk.END)
            self.health_text.insert(tk.END, f"Watchdog: Stall count {pulse['payload']['count']}")

    def inject_pulse(self):
        tokens = [int(x) for x in self.inject_entry.get().split(",") if x.strip().isdigit()]
        if tokens:
            asyncio.create_task(self.mesh.inject(tokens=tokens, origin=None))
            self.inject_entry.delete(0, tk.END)
            logging.info(f"GUI: Injected pulse with tokens {tokens}")

    async def run(self):
        # Start watchdog
        asyncio.create_task(self.watchdog.monitor())
        # Run Tkinter main loop in a separate thread
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.mainloop)

    def on_closing(self):
        asyncio.create_task(self.shutdown())
        self.destroy()

    async def shutdown(self):
        await self.sensor.stop()
        logging.info("GUI: System shutdown complete")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = FractalMeshGUI()
    asyncio.run(app.run())
```
