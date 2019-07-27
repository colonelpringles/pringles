from typing import List, cast

from colonel.models import Atomic, Coupled, Model, Link


class MaSerializer:
    @staticmethod
    def atomic_to_ma(atomic: Atomic) -> str:
        ma = f"[{atomic.name}]\n"
        for param, value in atomic.model_params.items():
            ma += f"{param}: {value}\n"
        return ma

    @classmethod
    def coupled_to_ma(cls, coupled: Coupled) -> str:
        ma = (
            f"[{coupled.name}]\n"
            f"components: {' '.join([str(c) for c in coupled.subcomponents])}\n"
            f"out: {' '.join([str(o) for o in coupled.outports])}\n"
            f"in: {' '.join([str(i) for i in coupled.inports])}\n"
        )
        links = (cast(List[Link], coupled.eic) +
                 cast(List[Link], coupled.ic) +
                 cast(List[Link], coupled.eoc))
        for link in links:
            ma += f"link: {link.from_port.get_identifier_for(coupled)} "
            ma += f"{link.to_port.get_identifier_for(coupled)}\n"
        for model in coupled.subcomponents:
            ma += f"\n\n{cls.model_to_ma(model)}"
        return ma

    @classmethod
    def model_to_ma(cls, model: Model) -> str:
        if isinstance(model, Atomic):
            return cls.atomic_to_ma(cast(Atomic, model))
        else:
            return cls.coupled_to_ma(cast(Coupled, model))

    @classmethod
    def serialize(cls, model: Model) -> str:
        return cls.model_to_ma(model)
