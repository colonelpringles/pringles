from __future__ import annotations

import os
import tempfile
import uuid
import pickle
from datetime import datetime
from typing import Optional, List

import pandas as pd
import matplotlib.pyplot as plt  # pylint: disable=E0401
from matplotlib.axes import Axes  # pylint: disable=E0401

from pringles.models import Model
from pringles.utils import VirtualTime
from pringles.simulator.events import Event
from pringles.simulator.errors import AttributeIsImmutableException, TopModelNotNamedTopException


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
        """
        A Simulation is the object you later simulate
        :param top_model: The top model of the simulation
        :type top_model: Model
        :param duration: Simulation duration, defaults to None (until models passivate)
        :type duration: Optional[VirtualTime], optional
        :param events: List of external events, defaults to None
        :type events: Optional[List[Event]], optional
        :param use_simulator_logs: True if simulator logs should be generated, defaults to True
        :type use_simulator_logs: bool, optional
        :param use_simulator_out: True if simulator outputs should be captured, defaults to True
        :type use_simulator_out: bool, optional
        :param working_dir: Working directory in which to dump all "compiled"
            models, logs, outputs and events file, defaults to None, in which case
            a temporal directory is created, in an OS-specific location.
        :type working_dir: Optional[str], optional
        :param override_logged_messages: ADVANCED USE. Override logged messages filter.
        :type override_logged_messages: Optional[str], optional
        """
        self.result: Optional[SimulationResult] = None

        self.assert_top_model_named_top(top_model)
        self._top_model = top_model
        self._events = events
        self._duration = duration
        self._use_simulator_logs = use_simulator_logs
        self._use_simulator_out = use_simulator_out
        self._override_logged_messages = override_logged_messages

        self._working_dir = working_dir if working_dir else tempfile.mkdtemp()
        self._output_dir = self.make_output_dir(self.working_dir)

    @property
    def top_model(self):
        return self._top_model

    @top_model.setter
    def top_model(self, val):
        raise AttributeIsImmutableException()

    @property
    def events(self):
        return self._events

    @events.setter
    def events(self, val):
        raise AttributeIsImmutableException()

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, val):
        raise AttributeIsImmutableException()

    @property
    def use_simulator_logs(self):
        return self._use_simulator_logs

    @use_simulator_logs.setter
    def use_simulator_logs(self, val):
        raise AttributeIsImmutableException()

    @property
    def use_simulator_out(self):
        return self._use_simulator_out

    @use_simulator_out.setter
    def use_simulator_out(self, val):
        raise AttributeIsImmutableException()

    @property
    def override_logged_messages(self):
        return self._override_logged_messages

    @override_logged_messages.setter
    def override_logged_messages(self, val):
        raise AttributeIsImmutableException()

    @property
    def working_dir(self):
        return self._working_dir

    @working_dir.setter
    def working_dir(self, val):
        raise AttributeIsImmutableException()

    @property
    def output_dir(self):
        return self._output_dir

    @output_dir.setter
    def output_dir(self, val):
        raise AttributeIsImmutableException()

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
            path = self.output_dir + '/' + self.DEFAULT_PICKLEFILE_NAME
        pickle.dump(self, open(path, "wb"))

    @classmethod
    def read_pickle(cls, path) -> Simulation:
        a_simulation = pickle.load(open(path, "rb"))
        assert isinstance(a_simulation, Simulation)
        return a_simulation

    def assert_top_model_named_top(self, top_model: Model):
        if top_model.name != "top":
            raise TopModelNotNamedTopException()
