import pytest
from colonel.models import Event, Port
from colonel.utils import VirtualTime

sample_port = Port("sample_port", None)
one_hour_time = VirtualTime.of_hours(1)


@pytest.mark.parametrize("event,expected_serialization", [
    (Event(one_hour_time, sample_port, 1.5), "1:0:0:0 sample_port 1.5;"),
    (Event(one_hour_time, sample_port, 1), "1:0:0:0 sample_port 1;"),
    (Event(one_hour_time, sample_port, [1.5, 2.3]), "1:0:0:0 sample_port [1.5,2.3];"),
])
def test_event_serialized_correctly(event: Event, expected_serialization: str):
    assert event.serialize() == expected_serialization
