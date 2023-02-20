from cxr.state.state import StateManager, StateError
from cxr.state.qoid import Property
from datetime import datetime
import os


class StateTelemetryError(ValueError):
    """
    An exception which is thrown when an illegal variable-setting action occurs
    """


class StateTelemeter(StateManager):
    def __init__(self, key, name):
        super().__init__(key, name)
        self._device = None
        self.toggle_ser_priority(ser_first=False)
        self["telemetry"] = []
        self["nonser_telemetry"] = []
        self["stream_path"] = None
        self["stream_filename"] = name
        self["streaming"] = False
        self["stream_range"] = 100
        self["error_stream_range"] = 35

        @self.controller
        def controller(event):
            if self.current_state() == "playing":
                self.step(event)

        @self.add_state("playing")
        def playing(event):
            self.step(event)

        @self.add_state("crashed")
        def crashed(event):
            pass

    def device(self):
        if self._device is not None:
            return self._device
        else:
            raise StateTelemetryError(f"No device mounted to {self}")

    def mount(self, sm):
        """
        Attach a StateManager to the telemeter
        """
        if self._device is None:
            self._device = sm
        else:
            raise StateTelemetryError(f"Cannot mount {sm} to {self}; {self._device} is already mounted")

    def unmount(self):
        """
        Detach the mounted StateManager
        """
        if self._device:
            self._device = None
        else:
            raise StateTelemetryError(f"Nothing to unmount from {self}")

    def destroy(self):
        """
        Unmount and destroy the attached StateManager
        """
        if self._device:
            StateManager.delete(self._device)
            self._device = None
        else:
            raise StateTelemetryError(f"Nothing to destroy in {self}")

    def set_stream_path(self, stream_path):
        self["stream_path"] = stream_path
        path_split = os.path.split(stream_path)
        # self["stream_path"] = "\\".join(path_split)
        # self["stream_filename"] = path_split[-1]
        for i in range(len(path_split)):
            partial = "\\".join(path_split[:i+1])
            if not os.path.isdir(partial):
                os.mkdir(partial)

    def set_streaming(self, streaming):
        self["streaming"] = streaming

    def set_stream_range(self, stream_range):
        self["stream_range"] = stream_range

    def set_error_stream_range(self, error_stream_range):
        self["error_stream_range"] = error_stream_range

    def step(self, event):
        """
        Submit an event to the mounted StateManager and possibly record the results
        """
        try:
            q = self._device.qoid()[0]
            q.tag = datetime.now().strftime("%Y-%m-%d %H%M%S")
            q += Property("event", event)
            self.telemetry.append(q)
            self["nonser_telemetry"].append(dict(self._device._data._nonser))
            if len(self.telemetry) > self.stream_range:
                self["telemetry"] = self.telemetry[1:]
                self["nonser_telemetry"] = self.nonser_telemetry[1:]
            self._device(event)
            if self.streaming:
                with open(self.stream_path + f"\\{self.key}.cxr", "a+") as f:
                    f.write(str(q) + "\n")

        except Exception as exc:
            error_time = datetime.now().strftime("%Y-%m-%d %H%M%S")
            q = self._device.qoid()[0]
            q.tag = f"ERROR - {error_time} - {exc}"
            q += Property("event", event)
            self.telemetry.append(q)
            self.nonser_telemetry.append(self._device._data._nonser)
            if len(self.telemetry) > self.stream_range:
                self["telemetry"] = self.telemetry[1:]
                self["nonser_telemetry"] = self.nonser_telemetry[1:]
            if self.streaming:
                with open(self.stream_path + f"\\{self.key}-errors-{error_time}.cxr", "w+") as f:
                    for i in range(-(self.error_stream_range + 1), -1, -1):
                        f.write(str(self.telemetry[i]) + "\n")
                    f.write(str(q) + "\n")
            self.change_state("crashed")

    def reverse(self, steps):
        """
        Note: reassigns all variables as serialisable
        If you are not using parameterised saves, this could be an issue
        """
        if self.current_state() == "crashed":
            steps += 1
        q = self.telemetry[len(self.telemetry)-steps]
        self["telemetry"] = self.telemetry[:len(self.telemetry)-steps]

        for property in q:
            self._device[property.tag] = property.val

        q = self.nonser_telemetry[len(self.nonser_telemetry) - steps]
        self["nonser_telemetry"] = self.nonser_telemetry[:len(self.nonser_telemetry) - steps]

        for property in q:
            self._device[property] = q[property]

        self.change_state("playing")