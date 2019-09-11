"""
Test simulator docstring
"""
from __future__ import annotations

import os
import subprocess
import tempfile
import uuid
import logging
import pickle
from datetime import datetime
from typing import Optional, List

import pandas as pd
import matplotlib.pyplot as plt  # pylint: disable=E0401
from matplotlib.axes import Axes  # pylint: disable=E0401

from pringles.simulator.errors import SimulatorExecutableNotFound
from pringles.simulator.registry import AtomicRegistry
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


class Simulation:
    DEFAULT_PICKLEFILE_NAME = 'simulation.pkl'

    def __init__(self,
                 top_model: Model,
                 duration: Optional[VirtualTime] = None,
                 events: Optional[List[Event]] = None,
                 use_simulator_logs: bool = True,
                 use_simulator_out: bool = True,
                 working_dir: Optional[str] = None,
                 override_logged_messages: Optional[str] = None):
        self.result: Optional[SimulationResult] = None

        self.top_model = top_model
        self.duration = duration
        self.events = events
        self.use_simulator_logs = use_simulator_logs
        self.use_simulator_out = use_simulator_out
        self.override_logged_messages = override_logged_messages

        self.working_dir = working_dir if working_dir else tempfile.mkdtemp()
        self.output_dir = self.make_output_dir(self.working_dir)

    @staticmethod
    def make_output_dir(working_dir: str) -> str:
        output_dir_name = datetime.now().strftime("%Y-%m-%d-%H%M%S") + "-" + str(uuid.uuid4().hex)
        absolute_output_dir = os.path.join(working_dir, output_dir_name)
        os.mkdir(absolute_output_dir)
        return absolute_output_dir

    @property
    def was_executed(self) -> bool:
        return self.result is not None

    def to_pickle(self, path=None) -> None:
        if path is None:
            path = self.output_dir + self.DEFAULT_PICKLEFILE_NAME

        with open(path, 'w') as pickle_file:
            pickle_file.write(pickle.dumps(self))

    @classmethod
    def read_pickle(cls, path) -> Simulation:
        a_simulation = pickle.load(path)
        assert isinstance(a_simulation, Simulation)
        return a_simulation


class Simulator:
    CDPP_BIN = 'cd++'

    def __init__(self, cdpp_bin_path: str, user_models_dir: Optional[str] = None,
                 autodiscover=True):
        self.executable_route = self.find_executable_route(cdpp_bin_path)
        self.atomic_registry = AtomicRegistry(user_models_dir, autodiscover)

    # This is thread-safe mate.
    def run_simulation(self,
                       simulation: Simulation) -> SimulationResult:
        """Run the simulation in the targeted CD++ simulator instance.
        :raises SimulatorExecutableNotFound: CD++ executable was not found in the provided directory
        :return: A SimulationResult, containing all data concerning the simulation results.
        :rtype: SimulationResult
        """
        logged_messages = 'XY'
        if simulation.override_logged_messages is not None:
            logged_messages = simulation.override_logged_messages

        dumped_top_model_path = self.dump_model_in_file(simulation.top_model,
                                                        simulation.output_dir)
        commands_list = [self.executable_route,
                         "-m" + dumped_top_model_path,
                         "-L" + logged_messages]
        if simulation.duration is not None:
            commands_list.append("-t" + str(simulation.duration))

        if simulation.events is not None:
            events_list = simulation.events
            events_file_path = self.dump_events_in_file(events_list, simulation.output_dir)
            commands_list.append("-e" + events_file_path)

        # Simulation logs
        if simulation.use_simulator_logs:
            logs_path = Simulator._new_working_file_named(simulation.output_dir, "logs")
            commands_list.append("-l" + logs_path)

        # Simulation output file
        if simulation.use_simulator_out:
            output_path = Simulator._new_working_file_named(simulation.output_dir, "output")
            commands_list.append("-o" + output_path)

        process_result = subprocess.run(commands_list, capture_output=True, check=True)
        logging.debug("Results: %s", process_result.stdout)
        logging.debug("Logs path: %s", logs_path)
        logging.debug("Output path: %s", output_path)

        simulation.result = SimulationResult(process_result=process_result,
                                             main_log_path=logs_path,
                                             output_path=output_path)
        return simulation.result

    def get_registry(self):
        return self.atomic_registry

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
