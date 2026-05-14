import tkinter as tk
from core.xdf_visualizer import XdfVisualizer
from tkinter import filedialog, ttk


class XdfTab(ttk.Frame):
    def __init__(self, parent) -> None:
        super().__init__(parent)

        self.xdf_visualizer = XdfVisualizer(self._update_visualizer_data)

        xdf_controls = ttk.Frame(self)
        xdf_controls.pack(pady=10, padx=10, fill="x")

        xdf_btn = ttk.Button(xdf_controls, text="Open XDF File", command=self._open_xdf)
        xdf_btn.pack(side="left", padx=5)

        # Stream Selector
        ttk.Label(xdf_controls, text="Stream:").pack(side="left", padx=(10, 2))
        self.stream_combo = ttk.Combobox(xdf_controls, state="readonly", width=25)
        self.stream_combo.pack(side="left", padx=5)
        self.stream_combo.set(0)
        self.stream_combo.bind("<<ComboboxSelected>>", lambda _: self._update_xdf())

        # Channel Selector
        ttk.Label(xdf_controls, text="Channel:").pack(side="left", padx=(10, 2))
        self.channel_combo = ttk.Combobox(xdf_controls, state="readonly", width=10)
        self.channel_combo.pack(side="left", padx=5)
        self.channel_combo.set(0)
        self.channel_combo.bind("<<ComboboxSelected>>", lambda _: self._update_xdf())

        # Page
        ttk.Label(xdf_controls, text="Page:").pack(side="left", padx=(10, 2))
        self.page_spinbox = ttk.Spinbox(
            xdf_controls,
            from_=1,
            to=1,
            width=5,
            command=self._update_xdf,
        )
        self.page_spinbox.set(1)
        self.page_spinbox.pack(side="left", padx=5)
        self.page_spinbox.bind("<Return>", lambda _: self._update_xdf())

        # Total pages labels
        ttk.Label(xdf_controls, text="Total pages: ").pack(side="left", padx=(10, 2))
        self.total_pages_label = ttk.Label(xdf_controls)
        self.total_pages_label.pack(side="left", padx=(10, 2))

        # Total samples labels
        ttk.Label(xdf_controls, text="Total samples: ").pack(side="left", padx=(10, 2))
        self.total_samples_label = ttk.Label(xdf_controls)
        self.total_samples_label.pack(side="left", padx=(10, 2))

        # Text Display Area
        xdf_frame = ttk.Frame(self)
        xdf_frame.pack(pady=10, padx=10, fill="both", expand=True)

        xdf_scroll = ttk.Scrollbar(xdf_frame)
        xdf_scroll.pack(side="right", fill="y")

        self.xdf_text_area = tk.Text(
            xdf_frame,
            height=30,
            width=100,
            font=("Consolas", 9),
            yscrollcommand=xdf_scroll.set,
            wrap="none",
        )
        self.xdf_text_area.pack(side="left", fill="both", expand=True)
        xdf_scroll.config(command=self.xdf_text_area.yview)
        self.xdf_text_area.config(state="disabled")

        self.file_path = None

    """UI Actions"""

    def _open_xdf(self):
        self.file_path = filedialog.askopenfilename(
            title="Seleccionar archivo XDF",
            filetypes=(("XDF Files", "*.xdf"), ("Todos los archivos", "*.*")),
        )

        if not self.file_path:
            return

        contents = self.xdf_visualizer.open_xdf(self.file_path)
        self._set_text(contents)

    def _update_xdf(self):
        if not self.file_path:
            return

        stream_index = self._get_current_stream()
        channel_index = self._get_current_channel()
        page_index = self._get_current_page()

        contents = self.xdf_visualizer.read_xdf(stream_index, channel_index, page_index)
        self._set_text(contents)

    """UI Feedback Update"""

    def _update_visualizer_data(
        self,
        streams: list[str],
        channels: list[str],
        total_pages: int,
        total_samples: int,
    ):
        self.after(
            0,
            self._apply_visualizer_update,
            streams,
            channels,
            total_pages,
            total_samples,
        )

    def _apply_visualizer_update(
        self,
        streams: list[str],
        channels: list[str],
        total_pages: int,
        total_samples: int,
    ):
        self.stream_combo.config(values=streams)
        self.stream_combo.current(0)
        self.channel_combo.config(values=channels)
        self.channel_combo.current(0)
        self.page_spinbox["to"] = total_pages
        self.total_pages_label.configure(text=f"{total_pages}")
        self.total_samples_label.configure(text=f"{total_samples}")

    def _set_text(self, text: str):
        self.xdf_text_area.config(state="normal")
        self.xdf_text_area.delete("1.0", "end")
        self.xdf_text_area.insert("end", f"{text}")
        self.xdf_text_area.config(state="disabled")

    """Helper functions"""

    def _get_current_stream(self) -> int:
        return int(self.stream_combo.current())

    def _get_current_channel(self) -> int:
        return int(self.channel_combo.current())

    def _get_current_page(self) -> int:
        return int(self.page_spinbox.get()) - 1
