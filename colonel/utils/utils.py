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
        self.hours = int(hours)
        self.minutes = int(minutes)
        self.seconds = int(seconds)
        self.milliseconds = int(milliseconds)
        self.remainder = int(remainder)

    @classmethod
    def of_seconds(cls, seconds: int) -> VirtualTime:
        return cls(0, 0, seconds, 0, 0)

    @classmethod
    def of_minutes(cls, minutes: int) -> VirtualTime:
        return cls(0, minutes, 0, 0, 0)

    @classmethod
    def of_hours(cls, hours: int) -> VirtualTime:
        return cls(hours, 0, 0, 0, 0)

    @classmethod
    def parse(cls, timestr: str) -> VirtualTime:
        return cls(*[int(unit) for unit in timestr.split(':')])

    @classmethod
    def from_number(cls, num: int) -> VirtualTime:
        units = []
        for max_val in [10, 1000, 60, 60, 99]:
            units.append(num % max_val)
            num = int(num/max_val)
        return cls(*units)

    def to_number(self) -> float:
        return (self.remainder +
                10 * self. milliseconds +
                10 * 1000 * self.seconds +
                10 * 1000 * 60 * self.minutes +
                10 * 1000 * 60 * 60 * self.hours)

    def __float__(self) -> float:
        return float(self.to_number())

    def __str__(self):
        return (f"{self.hours:02d}:{self.minutes:02d}:" +
                f"{self.seconds:02d}:{self.milliseconds:03d}")

    def __repr__(self):
        return (f"VirtualTime({self.hours:02d}:{self.minutes:02d}:" +
                f"{self.seconds:02d}:{self.milliseconds:03d}:{self.remainder})")
