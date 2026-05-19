from tkinter import ttk


class GraphTab(ttk.Frame):
    def __init__(self, parent) -> None:
        super().__init__(parent)

        self.example_lbl = ttk.Label(self, text="Graph!!")
        self.example_lbl.pack(pady=100)
