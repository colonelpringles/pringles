from colonel.models import Model
from datetime import timedelta


class SimulationResult:
    pass


class Simulator:
    def simulate(self, top_model: Model, duration: timedelta) -> SimulationResult:
        raise NotImplementedError()

    @staticmethod
    def to_ftime(duration: timedelta) -> str:
        # f stands for fucking
        return ""
