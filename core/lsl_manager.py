from typing import Callable
import pylsl as lsl
from pylsl import StreamInfo
from mne_lsl.stream import StreamLSL
from threading import Thread


class LslManager:
    def __init__(self):
        self.streams_ui_update_callback = None
        self.recording_ui_updated_callback = None
        # Stream searching
        self.search_thread: Thread | None = None
        self.active_streams: list[StreamInfo]

        # Recording
        self.active_mne_streams: list[StreamLSL] = []

    """ Active Stream Scanning """

    def start_stream_search(self):
        self.search_thread = Thread(target=self.search_streams, daemon=True)
        self.search_thread.start()

    def stop_stream_search(self):
        if self.search_thread is not None:
            self.search_thread.join()
            self.search_thread = None

    def search_streams(self):
        self.active_streams = lsl.resolve_streams(1.0)

        if self.streams_ui_update_callback is None:
            print(f"Can't update UI: streams_ui_update_callback is None")
            return

        self.streams_ui_update_callback(self.active_streams)

        self.search_thread = None

    """ Active Stream Recording """

    def start_recording(self):
        if not self.active_streams:
            print("Unable to start recording if there are no active streams!")
            return

        self.active_mne_streams = []
        for stream in self.active_streams:
            try:
                mne_stream = StreamLSL(bufsize=10.0, name=stream.name())
                mne_stream.connect(acquisition_delay=0.01)
                self.active_mne_streams.append(mne_stream)
            except Exception as e:
                print(f"Falied to connect automatically to {stream.name()}: {e}")

        if self.recording_ui_updated_callback is None:
            print(f"Can't update UI: recording_ui_updated_callback is None")
            return

        self.recording_ui_updated_callback(True)
        print("Real-time LSL data collection started.")

    def stop_recording(self):
        if self.recording_ui_updated_callback is None:
            print(f"Can't update UI: recording_ui_updated_callback is None")
            return

        self.recording_ui_updated_callback(False)
        for mne_stream in self.active_mne_streams:
            mne_stream.disconnect()
        self.active_mne_streams.clear()
        print("MNE-LSL automatic collection threads stopped.")

    """ Setters """

    def set_streams_ui_update_callback(
        self, streams_ui_update_callback: Callable[[list[StreamInfo]], None]
    ):
        self.streams_ui_update_callback = streams_ui_update_callback

    def set_recording_ui_updated_callback(
        self, recording_ui_updated_callback: Callable[[bool], None]
    ):
        self.recording_ui_updated_callback = recording_ui_updated_callback
        pass
