from __future__ import annotations
from colonel.models import Model
from colonel.utils import Duration
from colonel.wrapper import Wrapper
from typing import Optional


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
