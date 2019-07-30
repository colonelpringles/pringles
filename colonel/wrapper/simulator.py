from __future__ import annotations
from colonel.models import Model
from colonel.utils import VirtualTime
from colonel.wrapper import Wrapper, SimulationResult
from typing import Optional


class Simulator:
    def __init__(self, *args, **kwargs):
        self.simulator_impl = Wrapper()

    def simulate(self, top_model: Model, duration: Optional[VirtualTime]) -> SimulationResult:
        return self.simulator_impl.run_simulation(top_model, str(duration))
