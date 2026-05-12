import pyxdf

_WIDTH_T = 12
_WIDTH_S = 30

_TITLE1 = "Timestamps"


def read_xdf(file_path: str, stream_index: int = 0, channel_index: int = 0) -> str:
    data, _ = pyxdf.load_xdf(rf"{file_path}")

    series = data[stream_index]["time_series"]
    timestamps = data[stream_index]["time_stamps"]

    lines = []
    lines.append(f"{_TITLE1:<{_WIDTH_T}} | Canal {channel_index:<{_WIDTH_S}}")
    lines.append("-" * (_WIDTH_T + _WIDTH_S + 3))

    for i in range(len(series)):
        val = series[i][channel_index]
        t = timestamps[i]

        lines.append(f"{t:<{_WIDTH_T}.4f} | {val:<{_WIDTH_S}.6f}")

    return "\n".join(lines)
