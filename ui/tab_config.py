from tkinter import ttk
import tkinter
import app_config as config


# TODO: LA MAYORIA DE OPCIONES SON DE TIRGNO CATEGORÍZALAS
class ConfigTab(ttk.Frame):
    def __init__(self, parent) -> None:
        super().__init__(parent)

        config_main_frame = ttk.Frame(self)
        config_main_frame.pack(expand=True, fill="both")

        config_container = ttk.LabelFrame(
            config_main_frame, text=" System Configuration "
        )
        # Added expand=True here
        config_container.pack(padx=20, pady=20, expand=True)

        v_num = (self.register(self._validate_only_numbers), "%S")
        v_ip = (self.register(self._validate_ip_chars), "%S")

        # Enable Trigno Module Checkbox
        ttk.Label(config_container, text="Enable Delsys Trigno Module:").grid(
            row=0, column=0, sticky="e", padx=5, pady=5
        )
        self.is_active = tkinter.BooleanVar(value=config.get_enable_trigno_module())
        trigno_module_check = ttk.Checkbutton(
            config_container, variable=self.is_active, text="(Needs restart)"
        )
        trigno_module_check.grid(row=0, column=1, sticky="w", padx=2, pady=5)

        # IP Address
        ttk.Label(config_container, text="IP Address:").grid(
            row=1, column=0, sticky="e", padx=5, pady=5
        )
        self.ip_ent = ttk.Entry(config_container, width=15)
        self.ip_ent.insert(0, config.get_ip())
        self.ip_ent.config(validate="key", validatecommand=v_ip)
        self.ip_ent.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Command Port
        ttk.Label(config_container, text="Command Port:").grid(
            row=2, column=0, sticky="e", padx=5, pady=5
        )
        self.cmd_ent = ttk.Entry(
            config_container, validate="key", validatecommand=v_num, width=15
        )
        self.cmd_ent.insert(0, str(config.get_cmd_port()))
        self.cmd_ent.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Data Port
        ttk.Label(config_container, text="Data Port:").grid(
            row=3, column=0, sticky="e", padx=5, pady=5
        )
        self.data_ent = ttk.Entry(
            config_container, validate="key", validatecommand=v_num, width=15
        )
        self.data_ent.insert(0, str(config.get_data_port()))
        self.data_ent.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # Interval Spinner
        ttk.Label(config_container, text="UI Update Interval (ms):").grid(
            row=4, column=0, sticky="e", padx=5, pady=5
        )
        self.ui_spin = ttk.Spinbox(
            config_container, from_=10, to=500, increment=10, width=13
        )
        self.ui_spin.set(config.get_update_interval())
        self.ui_spin.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        # Samples per page
        ttk.Label(config_container, text="Samples per page:").grid(
            row=5, column=0, sticky="e", padx=5, pady=5
        )
        self.samples_ent = ttk.Entry(
            config_container, validate="key", validatecommand=v_num, width=15
        )
        self.samples_ent.insert(0, str(config.get_samples_per_page()))
        self.samples_ent.grid(row=5, column=1, sticky="w", padx=5, pady=5)

        # Save Button
        save_btn = ttk.Button(
            config_main_frame,
            text="Save & Apply Settings",
            command=self._update_settings,
        )
        # Added expand=True here as well
        save_btn.pack(pady=20, expand=True)

    def _update_settings(self):
        ip = self.ip_ent.get().strip()
        cmd_port = self.cmd_ent.get().strip()
        data_port = self.data_ent.get().strip()
        update_interval = self.ui_spin.get().strip()
        samples_per_page = self.samples_ent.get().strip()
        enable_trigno_module = str(self.is_active.get())
        config.update_settings(
            ip=ip,
            cmd_port=cmd_port,
            data_port=data_port,
            enable_trigno_module=enable_trigno_module,
            update_interval=update_interval,
            samples_per_page=samples_per_page,
        )

    """Helper Functions"""

    def _validate_only_numbers(self, char):
        return char.isdigit()

    def _validate_ip_chars(self, char):
        return char.isdigit() or char == "."
