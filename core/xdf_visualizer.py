import app_config as config
from typing import Any, Callable
import pyxdf

# Custom Types
ConfigUpdateCallback = Callable[[list[str], list[str], int, int], None]
XdfFile = tuple[list[dict[str, Any]], dict[str, Any]]


class XdfVisualizer:
    def __init__(self, update_function: ConfigUpdateCallback):
        self._update_UI_callback = update_function

        self.current_file_path: str | None = None
        self.current_file: XdfFile | None = None

    def open_xdf(
        self,
        file_path: str,
    ) -> str:
        if self.is_new_file(file_path) or self.current_file is None:
            self.current_file_path = file_path
            self.current_file = pyxdf.load_xdf(rf"{file_path}")

        self.load_stream_data(0)
        return self.read_xdf(0, 0, 0)

    def load_stream_data(self, stream_index: int):
        if self.current_file is None or self.current_file_path is None:
            return f"Invalid or empty file at path '{self.current_file_path}'"

        streams = self.current_file[0]
        stream = streams[stream_index]

        stream_labels = [f"{i}: {s['info']['name'][0]}" for i, s in enumerate(streams)]
        chan_list = [str(i + 1) for i in range(int(stream["info"]["channel_count"][0]))]

        PAGE_SIZE = config.get_samples_per_page()
        total_samples = len(stream["time_series"])
        total_pages = (total_samples + PAGE_SIZE - 1) // PAGE_SIZE

        self._update_UI_callback(stream_labels, chan_list, total_pages, total_samples)

    def read_xdf(
        self, stream_index: int, channel_index: int, current_page_index: int
    ) -> str:
        if self.current_file is None or self.current_file_path is None:
            return f"Invalid or empty file at path '{self.current_file_path}'"

        self.load_stream_data(stream_index)

        streams = self.current_file[0]
        stream = streams[stream_index]
        info = stream["info"]
        lines = [
            f"PAGE:   {current_page_index + 1}",
            f"FILE:   {self.current_file_path.split('/')[-1]}",
            f"STREAM: {info['name'][0]}",
            f"LABEL:  Channel {channel_index + 1}",
            f"RATE:   {info['nominal_srate'][0]} Hz",
            "-" * 45,
            f"{'Timestamp':<15} | {'Value':<20}",
            "-" * 45,
        ]

        series = stream["time_series"]
        stamps = stream["time_stamps"]

        PAGE_SIZE = config.get_samples_per_page()
        start_index = current_page_index * PAGE_SIZE
        end_index = min(start_index + PAGE_SIZE, len(series))

        for i in range(start_index, end_index):
            val = series[i][channel_index]
            try:
                val_str = f"{float(val):.6f}"
            except (ValueError, TypeError):
                val_str = str(val)
            lines.append(f"{stamps[i]:<15.4f} | {val_str:<20}")

        if not lines[7:]:
            lines.append("No data for this page.")

        return "\n".join(lines)

    """Helper Functions"""

    def is_new_file(self, file_path: str) -> bool:
        return file_path is not None and file_path is not self.current_file_path
