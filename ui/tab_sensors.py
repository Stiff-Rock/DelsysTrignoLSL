from core.trigno_connector import TrignoConnector
from tkinter import ttk


class SensorsTab(ttk.Frame):
    def __init__(self, parent) -> None:
        super().__init__(parent)

        self.dtl = TrignoConnector(self._update_sensor_data)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=(30, 20))

        self.start_btn = ttk.Button(button_frame, text="Start", command=self._start)
        self.start_btn.pack(side="left", padx=5)

        self.stop_btn = ttk.Button(button_frame, text="Stop", command=self._stop)
        self.stop_btn.pack(side="left", padx=5)
        self.stop_btn.configure(state="disabled")

        labels_frame = ttk.LabelFrame(self, text=" ERM Readings (mV) ")
        labels_frame.pack(pady=10, padx=10, fill="both", expand=True)
        self.voltage_labels: list[ttk.Label] = []

        # Sensor readings labels
        for i in range(16):
            sensor_container = ttk.Frame(labels_frame)
            sensor_container.grid(
                row=i // 4, column=i % 4, padx=10, pady=10, sticky="nsew"
            )

            header_lbl = ttk.Label(
                sensor_container,
                text=f"Sensor {i + 1}",
                font=("Segoe UI", 9, "underline"),
            )
            header_lbl.pack()

            lbl = ttk.Label(
                sensor_container,
                text="+0.00000",
                width=15,
                font=("Consolas", 10, "bold"),
                anchor="center",
            )
            lbl.pack()

            labels_frame.grid_columnconfigure(i % 4, weight=1)
            self.voltage_labels.append(lbl)

        for r in range(4):
            labels_frame.grid_rowconfigure(r, weight=1)

        for c in range(4):
            labels_frame.grid_columnconfigure(c, weight=1)

    """Connector functions"""

    def _start(self):
        self.dtl.start_trigno()
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")

    def _stop(self):
        self.dtl.stop_trigno()
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

    """UI Feedback Update"""

    def _update_sensor_data(self, voltages: tuple[float, ...]):
        self.after(0, self._apply_sensor_update, voltages)

    def _apply_sensor_update(self, voltages):
        for i in range(len(voltages)):
            if i < len(self.voltage_labels):
                self.voltage_labels[i].config(text=f"{voltages[i]:>+1.5f}")

    """Callbacks"""

    def shutdown_trigno(self):
        self.dtl.stop_trigno()
