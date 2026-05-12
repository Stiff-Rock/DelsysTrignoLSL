import pyxdf

data, header = pyxdf.load_xdf(
    r"C:\Users\Yago\Desktop\CurrentStudy\exp001\block_Default.xdf"
)

series = data[0]["time_series"]
timestamps = data[0]["time_stamps"]

width_t = 12
width_s = 30

title1 = "Timestamps"
title2 = "Series (Data)"

print(f"{title1:<{width_t}} | {title2:<{width_s}}")
print("-" * (width_t + width_s + 3))

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

for i in range(len(series)):
    s = series[i]

    color = ""
    if "Released" in str(s):
        color = RED
    elif "Pressed" in str(s):
        color = GREEN

    t = timestamps[i]
    print(f"{t:<{width_t}.4f} | {color}{str(s):<{width_s}}{RESET}")
    print("-" * (width_t + width_s + 3))
