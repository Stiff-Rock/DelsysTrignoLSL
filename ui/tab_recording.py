from tkinter import ttk


class RecordingTab(ttk.Frame):
    def __init__(self, parent) -> None:
        super().__init__(parent)

        self.start_btn = ttk.Button(self, text="Start")
        self.start_btn.pack(side="left", padx=5)
