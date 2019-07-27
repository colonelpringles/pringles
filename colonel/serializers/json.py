import json

from typing import cast

from colonel.models import Atomic, Coupled, Model, Port


class JsonSerializer:
    @staticmethod
    def outport_to_dict(port: Port) -> dict:
        return {
            'name': port.name,
            'message_type': 'Any',
            'kind': 'out'
        }

    @staticmethod
    def inport_to_dict(port: Port) -> dict:
        return {
            'name': port.name,
            'message_type': 'Any',
            'kind': 'in'
        }

    @classmethod
    def atomic_to_dict(cls, atomic: Atomic) -> dict:
        return {
            'id': atomic.name,
            'type': 'atomic',
            'ports': {
                'out': [cls.outport_to_dict(outport) for outport in atomic.outports],
                'in': [cls.inport_to_dict(inport) for inport in atomic.inports]
            }
        }

    @classmethod
    def coupled_to_dict(cls, coupled: Coupled) -> dict:
        return {
            'id': coupled.name,
            'type': 'coupled',
            'models': [cls.model_to_dict(model) for model in coupled.subcomponents],
            'ports': {
                'out': [cls.outport_to_dict(outport) for outport in coupled.outports],
                'in': [cls.inport_to_dict(inport) for inport in coupled.inports]
            },
            'eoc': [
                {
                    'to_port': coupling.to_port.name,
                    'from_port': coupling.from_port.name,
                    'from_model': coupling.from_port.owner.name
                }
                for coupling in coupled.eoc
            ],
            'eic': [
                {
                    'to_port': coupling.to_port.name,
                    'to_model': coupling.to_port.owner.name,
                    'from_port': coupling.from_port.name
                }
                for coupling in coupled.eic
            ],
            'ic': [
                {
                    'to_port': coupling.to_port.name,
                    'to_model': coupling.to_port.owner.name,
                    'from_port': coupling.from_port.name,
                    'from_model': coupling.from_port.owner.name
                }
                for coupling in coupled.ic
            ]
        }

    @classmethod
    def model_to_dict(cls, model: Model) -> dict:
        if isinstance(model, Atomic):
            return cls.atomic_to_dict(cast(Atomic, model))
        else:
            return cls.coupled_to_dict(cast(Coupled, model))

    @classmethod
    def serialize(cls, model: Model) -> str:
        return json.dumps(cls.model_to_dict(model))
