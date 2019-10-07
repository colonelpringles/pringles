import os
from typing import List, Tuple
import pytest  # noqa
from pringles.utils import VirtualTime
from pringles.models import Coupled, Model, AtomicModelBuilder
from pringles.simulator import Event, Simulator

CDPP_BIN_PATH = os.path.join(os.path.dirname(__file__), '../cdpp/src/bin/')

@pytest.fixture
def empty_coupled() -> Model:
    return Coupled("empty_coupled", [])

@pytest.fixture(scope='function')
def a_simulator() -> Simulator:
    return Simulator(CDPP_BIN_PATH)

@pytest.fixture(scope='function')
def queue_top_model_with_events() -> Tuple[Model, List[Event]]:
    Queue = AtomicModelBuilder().with_name("Queue").build()
    queue = Queue("queue", preparation="0:0:5:0")
    queue.add_inport("in").add_outport("out")
    top_model = Coupled("top", [queue])\
        .add_inport("incoming_event")\
        .add_outport("emitted_signal")\
        .add_coupling(queue.get_port("out"), "emitted_signal")\
        .add_coupling("incoming_event", queue.get_port("in"))

    incoming_event_port = top_model.get_port("incoming_event")

    events = [
        Event(VirtualTime.of_seconds(10), incoming_event_port, 1.5),
        Event(VirtualTime.of_seconds(20), incoming_event_port, 20.),
        Event(VirtualTime.of_seconds(30), incoming_event_port, 20.),
    ]

    yield top_model, events

    # Teardown code
    import pringles.models.models as models_module
    del models_module.Queue
