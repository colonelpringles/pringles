import os

from colonel.wrapper.errors import SimulatorExecutableNotFound

from colonel.wrapper.config import CDPP_BIN_PATH


class Wrapper:
    CDPP_BIN = 'cd++'

    def __init__(self):
        self.executable_route = self.discover_executable_route()

    def discover_executable_route(self) -> str:
        filepath = os.path.join(CDPP_BIN_PATH, self.CDPP_BIN)
        is_simulator_executable_present = os.path.isfile(filepath) \
            and os.access(filepath, os.X_OK)

        if is_simulator_executable_present is None:
            raise SimulatorExecutableNotFound()
        return filepath
