from tkinter import ttk
from core.lsl_manager import LslManager


class GraphTab(ttk.Frame):
    def __init__(self, parent, lsl_manager: LslManager) -> None:
        super().__init__(parent)

        self.is_recording = False

        self.lsl_manager = lsl_manager
        self.lsl_manager.set_recording_ui_updated_callback(
            self._on_is_recording_changed
        )

        self.example_lbl = ttk.Label(self, text="Graph!!")
        self.example_lbl.pack(pady=20)

    def _on_is_recording_changed(self, is_recording: bool):
        self.after(0, self._toggle_is_recording, is_recording)

    def _toggle_is_recording(self, is_recording: bool):
        self.is_recording = is_recording

        if self.is_recording:
            self.update_ui_plots()

    def update_ui_plots(self):
        if self.is_recording:
            for stream in self.lsl_manager.active_mne_streams:
                n_new = stream.n_new_samples
                if n_new > 0:
                    data, timestamps = stream.get_data(
                        winsize=n_new / stream.info["sfreq"]
                    )
                    self.example_lbl.config(text=f"{data} at {timestamps}")

        self.after(40, self.update_ui_plots)
