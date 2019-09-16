import pytest
import os

from pringles.utils import VirtualTime
from pringles.simulator import Simulation
from pringles.simulator.errors import AttributeIsImmutableException, TopModelNotNamedTopException


def test_to_pickle_generates_file_in_output_dir(queue_top_model_with_events):
    a_model, events = queue_top_model_with_events
    a_simulation = Simulation(top_model=a_model,
                              events=events)
    assert len(os.listdir(a_simulation.output_dir)) == 0
    a_simulation.to_pickle()
    assert len(os.listdir(a_simulation.output_dir)) == 1

def test_to_pickle_and_read_pickle_gets_the_same_simulation(queue_top_model_with_events):
    a_model, events = queue_top_model_with_events
    a_simulation = Simulation(top_model=a_model,
                              events=events)
    a_simulation.to_pickle()
    unpickled_simulation = Simulation.read_pickle(
        a_simulation.output_dir + '/' + Simulation.DEFAULT_PICKLEFILE_NAME)
    assert a_simulation.top_model.name == unpickled_simulation.top_model.name

def test_simulation_with_top_model_not_named_top_raises(queue_top_model_with_events):
    a_model, _ = queue_top_model_with_events
    a_model.name = 'low'
    with pytest.raises(TopModelNotNamedTopException):
        Simulation(top_model=a_model)

def test_top_model_and_events_of_simulation_are_immutable(queue_top_model_with_events, empty_coupled):
    a_model, events = queue_top_model_with_events
    a_simulation = Simulation(top_model=a_model,
                              events=events)

    # Get attribute works
    assert a_simulation.top_model == a_model
    assert a_simulation.events == events

    with pytest.raises(AttributeIsImmutableException):
        a_simulation.top_model = empty_coupled

    with pytest.raises(AttributeIsImmutableException):
        a_simulation.events = []

def test_simulation_options_are_immutable(queue_top_model_with_events):
    a_model, events = queue_top_model_with_events

    duration = VirtualTime.of_seconds(3)
    use_simulator_logs = True
    use_simulator_out = True
    working_dir = '/tmp/'
    override_logged_messages = False

    a_simulation = Simulation(top_model=a_model,
                              events=events,
                              duration=duration,
                              use_simulator_logs=use_simulator_logs,
                              use_simulator_out=use_simulator_out,
                              working_dir=working_dir,
                              override_logged_messages=override_logged_messages)

    # Get attribute works
    assert a_simulation.duration == duration
    assert a_simulation.use_simulator_logs == use_simulator_logs
    assert a_simulation.use_simulator_out == use_simulator_out
    assert a_simulation.working_dir == working_dir
    assert a_simulation.override_logged_messages == override_logged_messages
    assert a_simulation.working_dir in a_simulation.output_dir

    with pytest.raises(AttributeIsImmutableException):
        a_simulation.duration = VirtualTime.of_minutes(2)
    with pytest.raises(AttributeIsImmutableException):
        a_simulation.use_simulator_logs = False
    with pytest.raises(AttributeIsImmutableException):
        a_simulation.use_simulator_out = False
    with pytest.raises(AttributeIsImmutableException):
        a_simulation.working_dir = 'potato'
    with pytest.raises(AttributeIsImmutableException):
        a_simulation.override_logged_messages = True
    with pytest.raises(AttributeIsImmutableException):
        a_simulation.output_dir = 'tomato'
