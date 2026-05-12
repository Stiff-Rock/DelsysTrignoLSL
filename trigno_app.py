import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from xdf_visualizer import read_xdf
from trigno_connector import TrignoConnector
import app_config as config

WIDTH = 1100
HEIGHT = 800


class TrignoApp:
    def __init__(self):
        config.load_settings()
        self.dtl = TrignoConnector(self._update_sensor_data)

        self.root = tk.Tk()
        self.root.title("Delsys Control Utility")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (WIDTH // 2)
        y = (screen_height // 2) - (HEIGHT // 2)
        self.root.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")

        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        ttk.Style(self.root).theme_use("vista")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.tab_sensors = ttk.Frame(self.notebook)
        self.tab_xdf = ttk.Frame(self.notebook)
        self.tab_config = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_sensors, text=" Real-Time Sensors ")
        self.notebook.add(self.tab_xdf, text=" XDF File Viewer ")
        self.notebook.add(self.tab_config, text=" Settings ")

        # --- SENSORS ---
        self.start_btn = ttk.Button(self.tab_sensors, text="Start", command=self._start)
        self.start_btn.pack(pady=10)

        self.stop_btn = ttk.Button(self.tab_sensors, text="Stop", command=self._stop)
        self.stop_btn.pack(pady=10)
        self.stop_btn.configure(state="disabled")

        self.subtitle_lbl = ttk.Label(
            self.tab_sensors,
            text="ERM Readings (mV)",
            font=("Segoe UI", 10, "bold underline"),
        )
        self.subtitle_lbl.pack(pady=(20, 10))

        self.labels_frame = ttk.Frame(self.tab_sensors)
        self.labels_frame.pack(pady=10, padx=10, fill="both", expand=True)
        self.voltage_labels: list[ttk.Label] = []

        for i in range(16):
            lbl = ttk.Label(
                self.labels_frame,
                text="+0.00000",
                width=20,
                font=("Consolas", 10, "bold"),
            )
            lbl.grid(row=i // 4, column=i % 4, padx=5, pady=5)
            self.labels_frame.grid_columnconfigure(i % 4, weight=1)
            self.voltage_labels.append(lbl)

        # --- XDF Reader ---
        self.xdf_btn = ttk.Button(
            self.tab_xdf, text="Open XDF File", command=self._open_xdf
        )
        self.xdf_btn.pack(pady=10)

        self.xdf_frame = ttk.Frame(self.tab_xdf)
        self.xdf_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.xdf_scroll = ttk.Scrollbar(self.xdf_frame)
        self.xdf_scroll.pack(side="right", fill="y")

        self.xdf_text_area = tk.Text(
            self.xdf_frame,
            height=30,
            width=100,
            font=("Consolas", 9),
            yscrollcommand=self.xdf_scroll.set,
            wrap="none",
        )
        self.xdf_text_area.pack(side="left", fill="both", expand=True)
        self.xdf_scroll.config(command=self.xdf_text_area.yview)
        self.xdf_text_area.config(state="disabled")

        # --- CONFIGURATION ---
        self.config_container = ttk.LabelFrame(
            self.tab_config, text=" System Configuration "
        )
        self.config_container.pack(padx=20, pady=20, fill="x")

        v_num = (self.root.register(self._validate_only_numbers), "%S")
        v_ip = (self.root.register(self._validate_ip_chars), "%S")

        # IP Address
        ttk.Label(self.config_container, text="IP Address:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.ip_ent = ttk.Entry(self.config_container)
        self.ip_ent.insert(0, config.get_ip())
        v_ip = (self.root.register(self._validate_ip_chars), "%S")
        self.ip_ent.config(validate="key", validatecommand=v_ip)
        self.ip_ent.grid(row=0, column=1, padx=5, pady=5)

        # Command Port
        ttk.Label(self.config_container, text="Command Port:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.cmd_ent = ttk.Entry(
            self.config_container, validate="key", validatecommand=v_num
        )
        self.cmd_ent.insert(0, str(config.get_cmd_port()))
        self.cmd_ent.grid(row=1, column=1, padx=5, pady=5)

        # Data Port
        ttk.Label(self.config_container, text="Data Port:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        self.data_ent = ttk.Entry(
            self.config_container, validate="key", validatecommand=v_num
        )
        self.data_ent.insert(0, str(config.get_data_port()))
        self.data_ent.grid(row=2, column=1, padx=5, pady=5)

        # Interval Spinner
        ttk.Label(self.config_container, text="UI Update Interval (ms):").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        self.ui_spin = ttk.Spinbox(
            self.config_container, from_=10, to=500, increment=10
        )
        self.ui_spin.set(config.get_update_interval())
        self.ui_spin.grid(row=3, column=1, padx=5, pady=5)

        # Save Button
        save_btn = ttk.Button(
            self.tab_config,
            text="Save & Apply Settings",
            command=self._update_settings,
        )
        save_btn.pack(pady=20)

    def run(self):
        self.root.mainloop()

    def _start(self):
        self.dtl.start_trigno()
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")

    def _stop(self):
        self.dtl.stop_trigno()
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

    def _update_sensor_data(self, voltages: tuple[float, ...]):
        self.root.after(0, self._apply_update, voltages)

    def _apply_update(self, voltages):
        for i in range(len(voltages)):
            if i < len(self.voltage_labels):
                self.voltage_labels[i].config(text=f"{voltages[i]:>+1.5f}")

    def _open_xdf(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo XDF",
            filetypes=(("XDF Files", "*.xdf"), ("Todos los archivos", "*.*")),
        )

        if not file_path:
            return

        contents = read_xdf(file_path)
        self.xdf_text_area.config(state="normal")
        self.xdf_text_area.delete("1.0", "end")
        self.xdf_text_area.insert("end", f"{contents}")
        self.xdf_text_area.config(state="disabled")

    def _update_settings(self):
        ip = self.ip_ent.get().strip()
        cmd_port = self.cmd_ent.get().strip()
        data_port = self.data_ent.get().strip()
        update_interval = self.ui_spin.get().strip()

        config.update_settings(ip, cmd_port, data_port, update_interval)

    def _validate_only_numbers(self, char):
        return char.isdigit()

    def _validate_ip_chars(self, char):
        return char.isdigit() or char == "."

    def _on_closing(self):
        self.dtl.stop_trigno()
        self.root.destroy()


if __name__ == "__main__":
    app = TrignoApp()
    app.run()
