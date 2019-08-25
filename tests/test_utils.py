import pytest
from pringles.utils import VirtualTime
"""
@pytest.mark.parametrize("event,expected_serialization", [
    (Event(one_hour_time, sample_port, 1.5), "01:00:00:000 sample_port 1.5;"),
    (Event(one_hour_time, sample_port, 1), "01:00:00:000 sample_port 1;"),
    (Event(one_hour_time, sample_port, [1.5, 2.3]), "01:00:00:000 sample_port [1.5, 2.3];"),
])
def test_event_serialized_correctly(event: Event, expected_serialization: str):
    assert event.serialize() == expected_serialization
"""


def test_time_string_parsed_correctly():
    time_string = "03:04:04:001:1"
    vtime = VirtualTime.parse(time_string)
    assert vtime.hours == 3
    assert vtime.minutes == 4
    assert vtime.seconds == 4
    assert vtime.milliseconds == 1
    assert vtime.remainder == 1


def test_time_string_parsed_correctly_with_float_remainder():
    time_string = "03:04:04:001:0.484671"
    vtime = VirtualTime.parse(time_string)
    assert vtime.hours == 3
    assert vtime.minutes == 4
    assert vtime.seconds == 4
    assert vtime.milliseconds == 1
    assert vtime.remainder == 0.484671


def test_virtual_time_comparison():
    big_time = VirtualTime.of_hours(1)
    little_time = VirtualTime.of_seconds(1)
    assert big_time > little_time


def test_sting_representation_has_fixed_length():
    vtime = VirtualTime(0, 0, 0, 0, 0)
    assert str(vtime) == '00:00:00:000'
    assert repr(vtime) == 'VirtualTime(00:00:00:000:0)'


def test_virtual_times_representing_samee_value_should_be_equal():
    one_hour_time = VirtualTime.of_hours(1)
    another_one_hour_time = VirtualTime.of_hours(1)

    assert one_hour_time == another_one_hour_time
