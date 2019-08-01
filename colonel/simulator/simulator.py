"""
Test simulator docstring
"""
from __future__ import annotations

import os
import subprocess
import tempfile
# import logging

import pandas as pd
import matplotlib.pyplot as plt  # pylint: disable=E0401
from matplotlib.axes import Axes
from typing import Optional, List, Tuple, Type


from colonel.simulator.errors import SimulatorExecutableNotFound, DuplicatedAtomicException
from colonel.models import Model, Event, AtomicModelBuilder, Atomic
from colonel.serializers import MaSerializer
from colonel.utils import VirtualTime, AtomicMetadataExtractor
from colonel.utils.errors import MetadataParsingException


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
        return value.strip().startswith("[") and value.strip().endswith("]")

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

        ticks = axes.get_xticks()
        axes.set_xticklabels([VirtualTime.from_number(tick) for tick in ticks], rotation=90)

        axes.set_xlim(left=0)
        return axes


class AtomicRegistry:

    SUPPORTED_FILE_EXTENSIONS = [".cpp", ".hpp", ".h"]

    def __init__(self, user_models_dir: Optional[str] = None, autodiscover: bool = True):
        self.user_models_dir = user_models_dir
        self.discovered_atomics: List[Type[Atomic]] = []
        if autodiscover and user_models_dir is not None:
            self.discover_atomics()

    def _add_atomic_class_as_attribute(self, name: str, atomic_class: Type[Atomic]):
        if hasattr(self, name):
            raise DuplicatedAtomicException(name)
        setattr(self, name, atomic_class)

    def discover_atomics(self) -> None:
        assert self.user_models_dir is not None

        files_to_extract_from = []
        for filename in os.listdir(self.user_models_dir):
            filename_with_path = os.path.join(self.user_models_dir, filename)
            if os.path.isfile(filename_with_path):
                _, file_extension = os.path.splitext(filename)
                if file_extension in AtomicRegistry.SUPPORTED_FILE_EXTENSIONS:
                    files_to_extract_from.append(filename_with_path)

        # extract metadata from discovered source files
        for discovered_path in files_to_extract_from:
            with open(discovered_path, "r") as discovered_file:
                try:
                    discovered_metadata = AtomicMetadataExtractor(discovered_file).extract()
                except MetadataParsingException:
                    pass
                else:
                    atomic_class_builder = AtomicModelBuilder().with_name(discovered_metadata.name)
                    for name in discovered_metadata.input_ports:
                        atomic_class_builder.with_input_port(name)
                    for name in discovered_metadata.output_ports:
                        atomic_class_builder.with_output_port(name)
                    builded_class = atomic_class_builder.build()
                    self._add_atomic_class_as_attribute(discovered_metadata.name,
                                                        builded_class)
                    self.discovered_atomics.append(builded_class)


class Simulator:
    CDPP_BIN = 'cd++'
    CDPP_BIN_PATH = os.path.join(os.path.dirname(__file__), '../../bin/')
    # CDPP_BIN_PATH will be wrong if the class is moved to a different directory

    def __init__(self, user_models_dir: Optional[str] = None, autodiscover=True):
        self.executable_route = self.find_executable_route()
        self.atomic_registry = AtomicRegistry(user_models_dir, autodiscover)

    def get_registry(self):
        return self.atomic_registry

    # This is thread-safe mate.
    def run_simulation(self,
                       top_model: Model,
                       duration: Optional[VirtualTime] = None,
                       events: Optional[List[Event]] = None,
                       use_simulator_logs: bool = True,
                       use_simulator_out: bool = True):
        logged_messages = 'XY'
        commands_list = [self.executable_route,
                         "-m" + self.dump_model_in_file(top_model),
                         "-L" + logged_messages]
        if duration is not None:
            commands_list.append("-t" + str(duration))

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
        # logging.error("Results: %s", process_result.stdout)
        # logging.error("Logs path: %s", logs_path)
        # logging.error("Output path: %s", output_path)

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
