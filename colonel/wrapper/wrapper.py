from __future__ import annotations

import os
import subprocess
import tempfile
from typing import Optional
import logging

from colonel.wrapper.errors import SimulatorExecutableNotFound
from colonel.wrapper.config import CDPP_BIN_PATH
from colonel.models import Model


class Wrapper:
    CDPP_BIN = 'cd++'

    def __init__(self):
        self.executable_route = self.find_executable_route()

    def run_simulation(self,
                       top_model: Model,
                       duration: Optional[str] = None,
                       events_file: Optional[str] = None):
        commands_list = ["cd++", "-m" + self.dump_model_in_file(top_model)]
        if duration is not None:
            commands_list.append("-t" + duration)

        if events_file is not None:
            commands_list.append("-e" + events_file)
        
        logs_handle, logs_path = tempfile.mkstemp()
        os.close(logs_handle)
        commands_list.append("-l" + logs_path)

        process_result = subprocess.run(commands_list, capture_output=True, check=True)
        logging.error("Results: %s", process_result.stdout)
        logging.error("Logs path: %s", logs_path)

    def dump_model_in_file(self, model: Model) -> str:
        file_descriptor, path = tempfile.mkstemp()
        with open(path, "w") as model_file:
            model_file.write(model.to_ma())

        os.close(file_descriptor)
        return path

    def find_executable_route(self) -> str:
        filepath = os.path.join(CDPP_BIN_PATH, self.CDPP_BIN)
        is_simulator_executable_present = os.path.isfile(filepath) \
            and os.access(filepath, os.X_OK)

        if is_simulator_executable_present is None:
            raise SimulatorExecutableNotFound()
        return filepath

