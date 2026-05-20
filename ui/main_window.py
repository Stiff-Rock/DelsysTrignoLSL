import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import app_config as config
from ui.tab_graph import GraphTab
from ui.tab_sensors import SensorsTab
from ui.tab_config import ConfigTab
from ui.tab_xdf import XdfTab
from ui.tab_recording import RecordingTab
from core.lsl_manager import LslManager

WIDTH = 1100
HEIGHT = 400


class TrignoApp:
    def __init__(self):
        config.load_settings()

        self.root = tk.Tk()
        self.root.title("LSL Workstation")
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

        self.lsl_manager = LslManager()
        self.tab_recording = RecordingTab(self.notebook, self.lsl_manager)
        self.notebook.add(self.tab_recording, text=" LSL Recording ")

        self.tab_graph = GraphTab(self.notebook, self.lsl_manager)
        self.notebook.add(self.tab_graph, text=" Graph ")

        self.tab_xdf = XdfTab(self.notebook)
        self.notebook.add(self.tab_xdf, text=" XDF File Viewer ")

        self.tab_sensors = None
        if config.get_enable_trigno_module():
            self.tab_sensors = SensorsTab(self.notebook)
            self.notebook.add(self.tab_sensors, text=" Trigno Sensors ")

        self.tab_config = ConfigTab(
            self.notebook, self._toggle_dirty, self._on_config_updated
        )
        self.notebook.add(self.tab_config, text=" Settings ")

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changing)

        self._current_tab_id = self.notebook.select()
        self._lock_tab_change = False

    def run(self):
        self.root.mainloop()

    """Events"""

    def _toggle_dirty(self, is_ditry: bool):
        tab_name = " Settings "
        if is_ditry:
            tab_name += "* "
        self.notebook.tab(self.tab_config, text=tab_name)

    def _on_config_updated(self):
        if config.get_enable_trigno_module():
            self.tab_sensors = SensorsTab(self.notebook)
            self.notebook.insert(2, self.tab_sensors, text=" Trigno Sensors ")
        elif self.tab_sensors is not None:
            self.tab_sensors.shutdown_trigno()
            self.notebook.forget(self.tab_sensors)
            self.tab_sensors = None

    def _on_closing(self):
        if self.tab_sensors is not None:
            self.tab_sensors.shutdown_trigno()
        self.lsl_manager.stop_stream_search()
        self.root.destroy()

    def _on_tab_changing(self, _):
        if self._lock_tab_change:
            return

        new_tab_id = self.notebook.select()

        if (
            self._current_tab_id == str(self.tab_config)
            and self.tab_config.unsaved_changes
        ):
            self._lock_tab_change = True
            self.notebook.select(self._current_tab_id)
            messagebox.showwarning(
                title="Unsaved Settings Changes",
                message="Please save or discard your changes before leaving the Settings tab.",
            )
            self._lock_tab_change = False
            return

        self._current_tab_id = new_tab_id
