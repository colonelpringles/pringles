import pytest  # noqa
import os
from pringles.simulator.simulator import Simulator
from pringles.utils import VirtualTime
from pringles.models import Coupled, AtomicModelBuilder, Event


TEST_PATH_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
TEST_EXECUTABLE = os.path.join(TEST_PATH_DIRECTORY, Simulator.CDPP_BIN)
CDPP_BIN_EXECUTABLE_PATH = os.path.join(Simulator.CDPP_BIN_PATH, Simulator.CDPP_BIN)


def test_simulator_executable_found_in_library_defined_dir():
    simulator = Simulator()
    assert simulator.executable_route == CDPP_BIN_EXECUTABLE_PATH


def test_no_exception_raised_in_simulation():
    simulator = Simulator()

    Queue = AtomicModelBuilder().with_name("Queue").build()
    sample_queue = Queue("sample_queue", preparation="0:0:5:0")
    sample_queue.add_inport("in").add_outport("out")
    top_model = Coupled("top", [sample_queue])\
        .add_inport("incoming_event")\
        .add_outport("emitted_signal")\
        .add_coupling(sample_queue.get_port("out"), "emitted_signal")\
        .add_coupling("incoming_event", sample_queue.get_port("in"))

    incoming_event_port = top_model.get_port("incoming_event")

    events = [
        Event(VirtualTime.of_seconds(10), incoming_event_port, 1.5),
        Event(VirtualTime.of_seconds(20), incoming_event_port, 20.),
        Event(VirtualTime.of_seconds(30), incoming_event_port, 20.),
    ]

    simulator.run_simulation(top_model, events=events)
