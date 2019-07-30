from __future__ import annotations
from colonel.utils.errors import BadVirtualTimeValuesError


class VirtualTime:
    def __init__(self, hours: int, minutes: int, seconds: int, milliseconds: int, remainder: int):
        if minutes > 60:
            raise BadVirtualTimeValuesError(f"Minutes should be less that 60, but is {minutes}")
        if seconds > 60:
            raise BadVirtualTimeValuesError(f"Seconds should be less that 60, but is {seconds}")
        if milliseconds > 1000:
            raise BadVirtualTimeValuesError("Milliseconds should be less that 1000, " +
                                            f" but is {milliseconds}")
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.milliseconds = milliseconds
        self.remainder = remainder

    @staticmethod
    def of_seconds(seconds: int) -> VirtualTime:
        return VirtualTime(0, 0, seconds, 0, 0)

    @staticmethod
    def of_minutes(minutes: int) -> VirtualTime:
        return VirtualTime(0, minutes, 0, 0, 0)

    @staticmethod
    def of_hours(hours: int) -> VirtualTime:
        return VirtualTime(hours, 0, 0, 0, 0)

    def __str__(self):
        return "%d:%d:%d:%d" % (self.hours, self.minutes, self.seconds, self.milliseconds)
