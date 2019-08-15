import pytest
from pringles.models import Event, Port
from pringles.utils import VirtualTime

sample_port = Port("sample_port", None)
one_hour_time = VirtualTime.of_hours(1)


@pytest.mark.parametrize("event,expected_serialization", [
    (Event(one_hour_time, sample_port, 1.5), "01:00:00:000 sample_port 1.5;"),
    (Event(one_hour_time, sample_port, 1), "01:00:00:000 sample_port 1;"),
    (Event(one_hour_time, sample_port, [1.5, 2.3]), "01:00:00:000 sample_port [1.5, 2.3];"),
])
def test_event_serialized_correctly(event: Event, expected_serialization: str):
    assert event.serialize() == expected_serialization
