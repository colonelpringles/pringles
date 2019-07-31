"""
Test simulator docstring
"""
from __future__ import annotations

import os
import subprocess
import tempfile
from typing import Optional, List, Tuple
import logging
import pandas as pd

from colonel.simulator.errors import SimulatorExecutableNotFound
from colonel.models import Model, Event
from colonel.serializers import MaSerializer
from colonel.utils import VirtualTime


# This object should contain the following properties:
# - Whether or not the simulation was successful (Or maybe this should raise an error)
# - The parsed logs
# - The parsed output
# - Elapsed simulation time
# - Real time that the simulation took to be completed
class SimulationResult:
    TIME_COL = 'time'
    PORT_COL = 'port'
    VALUE_COL = 'value'
    MESSAGE_TYPE_COL = 'message_type'
    MODEL_ORIGIN_COL = 'model_origin'
    MODEL_DEST_COL = 'model_dest'

    def __init__(self, process_result, main_log_path=None, output_path=None):
        self.process_result = process_result
        self.main_log_path = main_log_path
        self.output_path = output_path
        if self.successful():
            self.output_df = SimulationResult.parse_output_file(output_path)
            self.logs_dfs = SimulationResult.parse_main_log_file(main_log_path)

    def successful(self):
        return self.process_result.returncode == 0

    @classmethod
    def parse_output_file(cls, file_path):
        return pd.read_csv(file_path, delimiter=r'\s+',
                           names=[cls.TIME_COL, cls.PORT_COL, cls.VALUE_COL])

    @staticmethod
    def _is_list_value(value: str) -> bool:
        return '[' in value and ']' in value

    @staticmethod
    def _list_str_to_list(value: str) -> Tuple[float, ...]:
        # We use tuple because it hay to be hashable to be used in a Dataframe
        return tuple(float(num) for num in value.replace('[', '').replace(']', '').split(', '))

    @classmethod
    def parse_main_log_file(cls, file_path):
        log_file_per_component = {}
        parsed_logs = {}
        with open(file_path, 'r') as main_log_file:
            main_log_file.readline()  # Ignore first line
            log_dir = os.path.dirname(file_path)
            for line in main_log_file:
                name, path = line.strip().split(' : ')
                log_file_per_component[name] = path if os.path.isabs(path) else log_dir + '/' + path

        df_converters = {
            cls.VALUE_COL: lambda x: cls._list_str_to_list(x) if cls._is_list_value(x) else x,
            cls.TIME_COL: lambda x: VirtualTime.parse(x)
        }
        for logname, filename in log_file_per_component.items():
            parsed_logs[logname] = pd.read_csv(filename,
                                               delimiter=r' /\s+',
                                               engine='python',  # C engine doesnt work for regex
                                               converters=df_converters,
                                               names=[0, 1,  # Not sure what first two cols are
                                                      cls.MESSAGE_TYPE_COL,
                                                      cls.TIME_COL,
                                                      cls.MODEL_ORIGIN_COL,
                                                      cls.PORT_COL,
                                                      cls.VALUE_COL,
                                                      cls.MODEL_DEST_COL])
        return parsed_logs


class Simulator:
    CDPP_BIN = 'cd++'
    CDPP_BIN_PATH = os.path.join(os.path.dirname(__file__), '../../cdpp/src/bin/')
    # CDPP_BIN_PATH will be wrong if the class is moved to a different directory

    def __init__(self):
        self.executable_route = self.find_executable_route()

    def run_simulation(self,
                       top_model: Model,
                       duration: Optional[str] = None,
                       events: Optional[List[Event]] = None,
                       use_simulator_logs: bool = True,
                       use_simulator_out: bool = True):
        logged_messages = 'XY'
        commands_list = [self.executable_route,
                         "-m" + self.dump_model_in_file(top_model),
                         "-L" + logged_messages]
        if duration is not None:
            commands_list.append("-t" + duration)

        if events is not None:
            events_list = events
            events_file_path = self.dump_events_in_file(events_list)
            commands_list.append("-e" + events_file_path)

        # Simulation logs
        if use_simulator_logs:
            logs_handle, logs_path = tempfile.mkstemp()
            os.close(logs_handle)
            commands_list.append("-l" + logs_path)

        # Simulation output file
        if use_simulator_out:
            output_handle, output_path = tempfile.mkstemp()
            os.close(output_handle)
            commands_list.append("-o" + output_path)

        process_result = subprocess.run(commands_list, capture_output=True, check=True)
        logging.error("Results: %s", process_result.stdout)
        logging.error("Logs path: %s", logs_path)
        logging.error("Output path: %s", output_path)

        return SimulationResult(process_result=process_result,
                                main_log_path=logs_path,
                                output_path=output_path)

    @staticmethod
    def dump_events_in_file(events: List[Event]) -> str:
        file_descriptor, path = tempfile.mkstemp()
        with open(path, "w") as events_file:
            for event in events:
                events_file.write(event.serialize() + "\n")

        os.close(file_descriptor)
        return path

    @staticmethod
    def dump_model_in_file(model: Model) -> str:
        file_descriptor, path = tempfile.mkstemp()
        with open(path, "w") as model_file:
            model_file.write(MaSerializer.serialize(model))

        os.close(file_descriptor)
        return path

    def find_executable_route(self) -> str:
        filepath = os.path.join(self.CDPP_BIN_PATH, self.CDPP_BIN)
        is_simulator_executable_present = os.path.isfile(filepath) \
            and os.access(filepath, os.X_OK)

        if is_simulator_executable_present is None:
            raise SimulatorExecutableNotFound()
        return filepath
