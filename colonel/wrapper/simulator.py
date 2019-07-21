from __future__ import annotations
from colonel.models import Model
from colonel.wrapper import Wrapper
from typing import Optional


class BadDurationValuesError(Exception):
    pass


class Duration:
    def __init__(self, hours: int, minutes: int, seconds: int, milliseconds: int, remainder: int):
        if minutes > 60:
            raise BadDurationValuesError(f"Minutes should be less that 60, but is {minutes}")
        if seconds > 60:
            raise BadDurationValuesError(f"Seconds should be less that 60, but is {seconds}")
        if milliseconds > 1000:
            raise BadDurationValuesError(f"Milliseconds should be less that 1000, but is {milliseconds}")
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.milliseconds = milliseconds
        self.remainder = remainder

    def __str__(self):
        return "%d:%d:%d:%d" % (self.hours, self.minutes, self.seconds, self.milliseconds)


# This object should contain the following properties:
# - Whether or not the simulation was successful (Or maybe this should raise an error)
# - The parsed logs
# - The parsed output
# - Elapsed simulation time
# - Real time that the simulation took to be completed
class SimulationResult:
    pass


class Simulator:
    def __init__(self, *args, **kwargs):
        self.simulator_impl = Wrapper()

    def simulate(self, top_model: Model, duration: Optional[Duration]) -> SimulationResult:
        self.simulator_impl.run_simulation(top_model, str(duration))
