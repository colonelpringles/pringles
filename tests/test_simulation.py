import pytest
import os
from pringles.simulator import Simulation
from pringles.simulator.errors import SimulationObjectIsInmutableException

from .utils import make_queue_top_model_with_events

def test_to_pickle_generates_file_in_output_dir():
    a_model, events = make_queue_top_model_with_events()
    a_simulation = Simulation(top_model=a_model,
                              events=events)
    assert len(os.listdir(a_simulation.output_dir)) == 0
    a_simulation.to_pickle()
    assert len(os.listdir(a_simulation.output_dir)) == 1

def test_to_pickle_and_read_pickle_gets_the_same_simulation():
    a_model, events = make_queue_top_model_with_events()
    a_simulation = Simulation(top_model=a_model,
                              events=events)
    a_simulation.to_pickle()
    unpickled_simulation = Simulation.read_pickle(
        a_simulation.output_dir + Simulation.DEFAULT_PICKLEFILE_NAME)
    assert a_simulation.top_model == unpickled_simulation.top_model
