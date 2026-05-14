import tkinter as tk
from tkinter import ttk
import app_config as config
from ui.tab_sensors import SensorsTab
from ui.tab_config import ConfigTab
from ui.tab_xdf import XdfTab

WIDTH = 1100
HEIGHT = 300


class TrignoApp:
    def __init__(self):
        config.load_settings()

        self.root = tk.Tk()
        self.root.title("Delsys Trigno LSL")
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        ttk.Style(self.root).theme_use("vista")

        # Set window size and center it
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (WIDTH // 2)
        y = (screen_height // 2) - (HEIGHT // 2)
        self.root.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")

        # Tab Set-up
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.tab_sensors = SensorsTab(self.notebook)
        self.tab_xdf = XdfTab(self.notebook)
        self.tab_config = ConfigTab(self.notebook)

        self.notebook.add(self.tab_sensors, text=" Real-Time Sensors ")
        self.notebook.add(self.tab_xdf, text=" XDF File Viewer ")
        self.notebook.add(self.tab_config, text=" Settings ")

    def run(self):
        self.root.mainloop()

    """Events"""

    def _on_closing(self):
        self.tab_sensors.shutdown_trigno()
        self.root.destroy()
