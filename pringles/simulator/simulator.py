"""
Test simulator docstring
"""
from __future__ import annotations

import os
import subprocess
import logging
from typing import Optional, List

from pringles.simulator.errors import SimulatorExecutableNotFound
from pringles.simulator.simulation import SimulationResult, Simulation
from pringles.simulator.registry import AtomicRegistry
from pringles.models import Model, Event
from pringles.serializers import MaSerializer


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
