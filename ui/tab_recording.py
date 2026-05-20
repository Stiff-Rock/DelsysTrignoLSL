from tkinter import ttk
from tkinter.ttk import Checkbutton
import tkinter
from pylsl import StreamInfo
from tkinter import BooleanVar, messagebox
from core.lsl_manager import LslManager


class RecordingTab(ttk.Frame):
    def __init__(self, parent, lsl_manager: LslManager) -> None:
        super().__init__(parent)

        self._checkbuttons: list[Checkbutton] = []
        self._check_vars: list[BooleanVar] = []
        self.lsl_manager = lsl_manager
        self.lsl_manager.set_streams_ui_update_callback(self._on_active_streams_updated)

        style = ttk.Style()
        background_col = "#ffffff"
        style.configure("Light.TLabelframe", background=background_col)
        style.configure("Light.TLabelframe.Label", background=background_col)
        style.configure("LightFrame.TLabel", background=background_col)
        style.configure("LightFrame.TCheckbutton", background=background_col)

        # Active Streams Scrollable Area
        streams_container = ttk.LabelFrame(
            self,
            text=" Active Streams ",
            width=300,
            height=150,
            style="Light.TLabelframe",
        )
        streams_container.pack_propagate(False)
        streams_container.pack(padx=10, pady=10, expand=True)
        canvas = tkinter.Canvas(
            streams_container,
            bg=background_col,
            highlightthickness=0,
        )
        scrollbar = ttk.Scrollbar(
            streams_container, orient="vertical", command=canvas.yview
        )
        self.scrollable_frame = tkinter.Frame(canvas, bg=background_col)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda _: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas_window = canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(canvas_window, width=e.width),
        )
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Buttons section
        self.rescan_btn = ttk.Button(
            self,
            text="Rescan",
            command=self._start_stream_search,
            takefocus=False,
        )
        self.rescan_btn.pack(pady=(0, 10))

        record_controls = ttk.Frame(self)
        record_controls.pack(pady=(10, 30), padx=10)

        self.start_btn = ttk.Button(
            record_controls,
            text="Start",
            command=self._start_recording,
            takefocus=False,
        )
        self.start_btn.pack(side="left", padx=5, pady=10)

        self.stop_btn = ttk.Button(
            record_controls,
            text="Stop",
            command=self._stop_recording,
            takefocus=False,
        )
        self.stop_btn.config(state="disabled")
        self.stop_btn.pack(side="left", padx=5, pady=10)

        self._start_stream_search()

    def _on_active_streams_updated(self, found_streams: list[StreamInfo]):
        self.after(0, self._update_streams_info, found_streams)

    def _update_streams_info(self, found_streams: list[StreamInfo]):
        self.rescan_btn.config(state="normal")
        if not found_streams:
            self._add_active_stream_entry("No Streams Found")
        elif found_streams:
            for stream in found_streams:
                self._add_active_stream_entry(stream.name())

    def _add_active_stream_entry(self, text: str):
        is_active = BooleanVar(value=False)
        self._check_vars.append(is_active)

        chck = ttk.Checkbutton(
            self.scrollable_frame,
            text=text,
            style="LightFrame.TCheckbutton",
            variable=is_active,
            takefocus=False,
        )
        self._checkbuttons.append(chck)

        chck.pack(anchor="w", padx=10, pady=5)

    def _start_stream_search(self):
        self.rescan_btn.config(state="disabled")
        self._empty_streams_container()
        self._check_vars.clear()
        self._checkbuttons.clear()
        self.lsl_manager.start_stream_search()

    def _empty_streams_container(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    def _start_recording(self):
        if len(self._check_vars) <= 0:
            messagebox.showwarning(
                title="No active streams detected",
                message="There are no active streams to record.",
            )
            return

        has_selected_streams = False
        for boolVar in self._check_vars:
            if boolVar.get() == True:
                has_selected_streams = True
                break

        if not has_selected_streams:
            messagebox.showwarning(
                title="No Streams Selected",
                message="Please select at least one active stream to start recording.",
            )
            return

        for button in self._checkbuttons:
            button.config(state="disabled")

        self.rescan_btn.config(state="disabled")
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.lsl_manager.start_recording()

    def _stop_recording(self):
        for button in self._checkbuttons:
            button.config(state="normal")
        self.rescan_btn.config(state="normal")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.lsl_manager.stop_recording()
