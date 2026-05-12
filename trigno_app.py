import tkinter as tk
from threading import Thread
from tkinter import ttk
import socket
import struct
from typing import Callable
from pylsl import StreamInfo, StreamOutlet, cf_float32

# Window settings
WIDTH = 800
HEIGHT = 200

# Trigno server settings
IP = "127.0.0.1"
CMD_PORT = 50040
DATA_PORT = 50041


class TrignoConnector:
    def __init__(self, update_function: Callable[[tuple[float, ...]], None]):
        self._update_UI_callback = update_function
        self._connected = False
        self._outlet = StreamOutlet(
            StreamInfo(
                "Delsys Trigno Base", "EMG", 16, 2000, cf_float32, "delsys_base_1"
            )
        )

        self.cmd_socket = None
        self.data_socket = None

    def start_trigno(self):
        if self._connected:
            return
        self._connected = True

        print("Starting Delsys Trigno Base Station...")
        Thread(target=self._connect_to_data_socket, daemon=True).start()
        Thread(target=self._connect_to_cmd_socket, daemon=True).start()

    def stop_trigno(self):
        print("Stopping Trigno connections...")
        self._connected = False
        if self.cmd_socket:
            try:
                self.cmd_socket.sendall(b"STOP\r\n\r\n")
                self.cmd_socket.close()
            except:
                pass

        if self.data_socket:
            try:
                self.data_socket.close()
            except:
                pass

    def _connect_to_cmd_socket(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.cmd_socket:
                self.cmd_socket.connect((IP, CMD_PORT))
                self.cmd_socket.sendall(b"START\r\n\r\n")
                print("Connected to CMD socket and started recording")

                # Recieve data from cmd socket
                while self._connected:
                    data = self.cmd_socket.recv(1024)
                    if not data or not self.cmd_socket:
                        break

                    print(f"\n==CMD SOCKET MSG==\n{data}", end="\n==END==\n\n")

                if self.cmd_socket:
                    self.cmd_socket.sendall(b"STOP\r\n\r\n")
        except (ConnectionAbortedError, OSError):
            pass
        except Exception as e:
            print(f"Unexpected error in CMD socket: {e}")
        finally:
            self.cmd_socket = None
            print("=== DISCONNECTED FROM CMD SOCKET ===")

    def _connect_to_data_socket(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.data_socket:
                self.data_socket.connect((IP, DATA_PORT))
                print("Connected to data socket")

                # Recieve data from data socket
                while self._connected:
                    data = self.data_socket.recv(1024)
                    if not data or not self.data_socket:
                        break

                    # Unpack binary data
                    for i in range(0, len(data) - (len(data) % 64), 64):
                        if not self._connected:
                            break

                        chunk = data[i : i + 64]
                        sensors_voltages: tuple[float, ...] = struct.unpack(
                            "<16f", chunk
                        )
                        print(
                            f"\n==DATA SOCKET MSG==\n{sensors_voltages}",
                            end="\n==END==\n\n",
                        )
                        self._update_UI_callback(sensors_voltages)
                        self._outlet.push_sample(sensors_voltages)
        except (ConnectionAbortedError, OSError):
            pass
        except Exception as e:
            print(f"Unexpected error in DATA socket: {e}")
        finally:
            self.data_socket = None
            print("=== DISCONNECTED FROM DATA SOCKET ===")


class TrignoApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Delsys Control Utility")

        # Center the window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (WIDTH // 2)
        y = (screen_height // 2) - (HEIGHT // 2)
        self.root.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")

        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        ttk.Style(self.root).theme_use("vista")

        self.start_btn = ttk.Button(self.root, text="Start", command=self._start)
        self.start_btn.pack(pady=10)

        self.stop_btn = ttk.Button(self.root, text="Stop", command=self._stop)
        self.stop_btn.pack(pady=10)
        self.stop_btn.configure(state="disabled")

        self.labels_frame = ttk.Frame(self.root)
        self.labels_frame.pack(pady=10, padx=10, fill="x")

        self.dtl = TrignoConnector(self._update_sensor_data)
        self.voltage_labels: list[ttk.Label] = []
        for i in range(16):
            lbl = ttk.Label(self.labels_frame, text="0.000", font=("Courier", 9))
            lbl.grid(row=0, column=i, padx=2)
            self.labels_frame.grid_columnconfigure(i, weight=1)
            self.voltage_labels.append(lbl)

    def run(self):
        self.root.mainloop()

    # Action functions
    def _start(self):
        self.dtl.start_trigno()
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")

    def _stop(self):
        self.dtl.stop_trigno()
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

    def _update_sensor_data(self, voltages: tuple[float, ...]):
        self.root.after(0, self._apply_update, voltages)

    def _apply_update(self, voltages):
        for i in range(16):
            self.voltage_labels[i].config(text=f"{voltages[i]:.3f}")

    def _on_closing(self):
        self.dtl.stop_trigno()
        self.root.destroy()


if __name__ == "__main__":
    app = TrignoApp()
    app.run()
