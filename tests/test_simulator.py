import pytest  # noqa
import os
import tempfile
from typing import List, Tuple
from pringles.simulator import Simulator, Simulation, SimulationResult
from pringles.simulator.errors import SimulatorExecutableNotFound
from pringles.utils import VirtualTime
from pringles.models import Coupled, Model, AtomicModelBuilder, Event
from tests.utils import make_queue_top_model_with_events


TEST_PATH_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
TEST_EXECUTABLE = os.path.join(TEST_PATH_DIRECTORY, Simulator.CDPP_BIN)
CDPP_BIN_PATH = os.path.join(os.path.dirname(__file__), '../cdpp/src/bin/')


def test_simulator_executable_found_in_library_defined_dir():
    simulator = Simulator(CDPP_BIN_PATH)
    cdpp_bin_executable_path = os.path.join(CDPP_BIN_PATH, Simulator.CDPP_BIN)
    assert simulator.executable_route == cdpp_bin_executable_path


def test_simulator_executable_not_found_raises():
    with pytest.raises(SimulatorExecutableNotFound):
        Simulator("a/fake/path")


def test_no_exception_raised_in_simulation():
    simulator = Simulator(CDPP_BIN_PATH)
    top_model, events = make_queue_top_model_with_events()
    simulation = Simulation(top_model=top_model, events=events)
    simulator.run_simulation(simulation)


def test_process_stdout_is_returned_correctly():
    simulator = Simulator(CDPP_BIN_PATH)
    top_model, events = make_queue_top_model_with_events()
    simulation = Simulation(top_model=top_model, events=events)
    simulation_result = simulator.run_simulation(simulation)
    assert simulation_result\
        .get_process_output()\
        .startswith("PCD++: A Tool to Implement n-Dimensional Cell-DEVS models")


def test_run_simulation_in_custom_wd():
    simulator = Simulator(CDPP_BIN_PATH)
    top_model, events = make_queue_top_model_with_events()
    temp_path = tempfile.mkdtemp()
    a_simulation = Simulation(top_model, events=events, working_dir=temp_path) 
    simulator.run_simulation(a_simulation)
    files_found = False
    for _, _, files in os.walk(temp_path):
        # Assert there are files
        files_found = len(files) > 0 if not files_found else files_found
        if not files_found:
            continue
        # Assert there's an event, logs, top_model and output file
        assert any([filename.startswith("top_model") for filename in files])
        assert any([filename.startswith("events") for filename in files])
        assert any([filename.startswith("logs") for filename in files])
        assert any([filename.startswith("output") for filename in files])
    assert files_found


def test_parse_output_file_float_values():
    with open('tests/resources/model_output_float_value', 'r') as out_file:
        output_dataframe = SimulationResult._parse_output_file(out_file)
        assert len(output_dataframe) == 3
        for time in output_dataframe[SimulationResult.TIME_COL]:
            assert isinstance(time, VirtualTime)
        for value in output_dataframe[SimulationResult.VALUE_COL]:
            assert isinstance(value, float)


def test_parse_output_file_tuple_values():
    with open('tests/resources/model_output_tuple_value', 'r') as out_file:
        output_dataframe = SimulationResult._parse_output_file(out_file)
        assert len(output_dataframe) > 0
        for time in output_dataframe[SimulationResult.TIME_COL]:
            assert isinstance(time, VirtualTime)
        for value in output_dataframe[SimulationResult.VALUE_COL]:
            assert isinstance(value, tuple)
            for coord in value:
                assert isinstance(coord, float)
