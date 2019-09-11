from typing import List, Tuple
import pytest  # noqa
from pringles.utils import VirtualTime
from pringles.models import Coupled, Model, AtomicModelBuilder, Event

def empty_coupled() -> Model:
    return Coupled("empty_coupled", [])

def make_queue_top_model_with_events() -> Tuple[Model, List[Event]]:
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

    return top_model, events
