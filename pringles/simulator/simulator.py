"""
Test simulator docstring
"""
from __future__ import annotations

import os
import subprocess
import tempfile
import uuid
import logging
from datetime import datetime
from typing import Optional, List

import pandas as pd
import matplotlib.pyplot as plt  # pylint: disable=E0401
from matplotlib.axes import Axes  # pylint: disable=E0401

from pringles.simulator.errors import SimulatorExecutableNotFound
from pringles.simulator.atomic_registry import AtomicRegistry
from pringles.models import Model, Event
from pringles.serializers import MaSerializer
from pringles.utils import VirtualTime


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

        if output_path:
            self.output_df = SimulationResult._parse_output_file(output_path)
        if main_log_path:
            self.logs_dfs = SimulationResult._parse_main_log_file(main_log_path)

    def successful(self):
        return self.process_result.returncode == 0

    @staticmethod
    def _parse_value(value: str):
        is_list = value.strip().startswith("[") and value.strip().endswith("]")
        if is_list:
            return tuple(float(num) for num in value.replace('[', '').replace(']', '').split(', '))
        return float(value)

    @classmethod
    def _parse_output_file(cls, file_path) -> pd.DataFrame:
        df_converters = {
            cls.VALUE_COL: cls._parse_value,
            cls.TIME_COL: VirtualTime.parse
        }
        return pd.read_csv(file_path,
                           delimiter=r'(?<!,)\s+',
                           engine='python',  # C engine doesnt work for regex
                           converters=df_converters,
                           names=[cls.TIME_COL, cls.PORT_COL, cls.VALUE_COL])

    @classmethod
    def _parse_main_log_file(cls, file_path):
        log_file_per_component = {}
        parsed_logs = {}
        with open(file_path, 'r') as main_log_file:
            main_log_file.readline()  # Ignore first line
            log_dir = os.path.dirname(file_path)
            for line in main_log_file:
                name, path = line.strip().split(' : ')
                log_file_per_component[name] = path if os.path.isabs(path) else log_dir + '/' + path

        df_converters = {
            cls.VALUE_COL: cls._parse_value,
            cls.TIME_COL: VirtualTime.parse
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

    def plot_port(self, logname: str, portname: str,
                  axes: Optional[Axes] = None, index=0) -> Optional[Axes]:
        log: pd.DataFrame = self.logs_dfs[logname]
        data_to_plot = log[log[self.PORT_COL] == portname]
        if data_to_plot.empty:
            return None
        if isinstance(data_to_plot[self.VALUE_COL][0], tuple):
            y_values = data_to_plot[self.VALUE_COL].map(lambda x: x[index])
        else:
            y_values = data_to_plot[self.VALUE_COL]

        if axes is None:
            axes = plt.axes()  # Create a new axes in current figure
        x_values = data_to_plot[self.TIME_COL]
        axes.plot(x_values, y_values)
        x_values_labels = [str(vtime) for vtime in sorted(x_values, key=float)]
        axes.set_xticklabels(x_values_labels, rotation=90)

        axes.set_xlim(left=0)
        return axes

    def get_process_output(self) -> str:
        """Returns the process STDOUT converted to string

        :return: the process STDOUT
        :rtype: str
        """
        return self.process_result.stdout.decode("utf-8")


class Simulator:
    CDPP_BIN = 'cd++'

    def __init__(self, cdpp_bin_path: str, user_models_dir: Optional[str] = None,
                 autodiscover=True):
        self.executable_route = self.find_executable_route(cdpp_bin_path)
        self.atomic_registry = AtomicRegistry(user_models_dir, autodiscover)

    def get_registry(self):
        return self.atomic_registry

    # This is thread-safe mate.
    def run_simulation(self,
                       top_model: Model,
                       duration: Optional[VirtualTime] = None,
                       events: Optional[List[Event]] = None,
                       use_simulator_logs: bool = True,
                       use_simulator_out: bool = True,
                       simulation_wd: Optional[str] = None,
                       override_logged_messages: Optional[str] = None) -> SimulationResult:
        """Run the simulation in the targeted CD++ simulator instance.

        :param top_model: The top model of the simulation to be ran
        :type top_model: Model
        :param duration: Simulation duration, defaults to None
        :type duration: Optional[VirtualTime], optional
        :param events: List of external events, defaults to None
        :type events: Optional[List[Event]], optional
        :param use_simulator_logs: True if simulator logs should be generated, defaults to True
        :type use_simulator_logs: bool, optional
        :param use_simulator_out: True if simulator outputs should be captured, defaults to True
        :type use_simulator_out: bool, optional
        :param simulation_wd: Working directory in which to dump all "compiled"
            models, logs, outputs and events file, defaults to None, in which case
            a temporal directory is created, in an OS-specific location.
        :type simulation_wd: Optional[str], optional
        :param override_logged_messages: ADVANCED USE. Override logged messages filter.
        :type override_logged_messages: Optional[str], optional
        :raises SimulatorExecutableNotFound: CD++ executable was not found in the provided directory
        :return: A SimulationResult, containing all data concerning the simulation results.
        :rtype: SimulationResult
        """
        logged_messages = 'XY'
        if override_logged_messages is not None:
            logged_messages = override_logged_messages

        if simulation_wd is not None:
            wd_simulation_subdirectory_name =\
                datetime.now().strftime("%Y-%m-%d-%H%M%S") + \
                "-" + str(uuid.uuid4().hex)
            simulation_wd = os.path.join(simulation_wd,
                                         wd_simulation_subdirectory_name)
            os.mkdir(simulation_wd)
        else:
            simulation_wd = tempfile.mkdtemp()

        dumped_top_model_path = self.dump_model_in_file(top_model,
                                                        simulation_wd)
        commands_list = [self.executable_route,
                         "-m" + dumped_top_model_path,
                         "-L" + logged_messages]
        if duration is not None:
            commands_list.append("-t" + str(duration))

        if events is not None:
            events_list = events
            events_file_path = self.dump_events_in_file(events_list, simulation_wd)
            commands_list.append("-e" + events_file_path)

        # Simulation logs
        if use_simulator_logs:
            logs_path = Simulator._new_working_file_named(simulation_wd, "logs")
            commands_list.append("-l" + logs_path)

        # Simulation output file
        if use_simulator_out:
            output_path = Simulator._new_working_file_named(simulation_wd, "output")
            commands_list.append("-o" + output_path)

        process_result = subprocess.run(commands_list, capture_output=True, check=True)
        logging.debug("Results: %s", process_result.stdout)
        logging.debug("Logs path: %s", logs_path)
        logging.debug("Output path: %s", output_path)

        return SimulationResult(process_result=process_result,
                                main_log_path=logs_path,
                                output_path=output_path)

    @staticmethod
    def dump_events_in_file(events: List[Event], simulation_wd: str) -> str:
        path = Simulator._new_working_file_named(simulation_wd, "events")
        with open(path, "w") as events_file:
            for event in events:
                events_file.write(event.serialize() + "\n")

        return path

    @staticmethod
    def _new_working_file_named(working_dir: str,
                                file_name: str) -> str:
        return os.path.join(working_dir, file_name)

    @staticmethod
    def dump_model_in_file(model: Model, custom_wd: str) -> str:
        path = Simulator._new_working_file_named(custom_wd, "top_model")
        with open(path, "w") as model_file:
            model_file.write(MaSerializer.serialize(model))

        return path

    def find_executable_route(self, cdpp_bin_path: str) -> str:
        filepath = os.path.join(cdpp_bin_path, self.CDPP_BIN)
        is_simulator_executable_present = os.path.isfile(filepath) \
            and os.access(filepath, os.X_OK)

        if not is_simulator_executable_present:
            raise SimulatorExecutableNotFound()
        return filepath
