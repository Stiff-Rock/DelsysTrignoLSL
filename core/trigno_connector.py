import socket
import struct
from typing import Callable
from pylsl import StreamInfo, StreamOutlet, cf_float32
from threading import Thread
import app_config as config


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

        self._sample_count = 0

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
                self.cmd_socket.connect((config.get_ip(), config.get_cmd_port()))
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
                self.data_socket.connect((config.get_ip(), config.get_data_port()))
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
                        self._outlet.push_sample(sensors_voltages)

                        self._sample_count += 1
                        if self._sample_count % config.get_update_interval() == 0:
                            if config.get_print_samples():
                                print(
                                    f"\n==DATA SOCKET MSG==\n{sensors_voltages}",
                                    end="\n==END==\n\n",
                                )
                            self._update_UI_callback(sensors_voltages)
        except (ConnectionAbortedError, OSError):
            pass
        except Exception as e:
            print(f"Unexpected error in DATA socket: {e}")
        finally:
            self.data_socket = None
            print("=== DISCONNECTED FROM DATA SOCKET ===")
