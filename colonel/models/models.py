from __future__ import annotations
from typing import List, cast, Any, Union


class PortNotFoundException(Exception):
    pass


class AtomicModelBuilder:
    def withName(self, name: str) -> AtomicModelBuilder:
        self.name = name
        return self

    def build(self) -> Any:
        return type(self.name, (Atomic,), {})


class Model:
    def __init__(self, name: str):
        self.name = name
        self.inports: List[Port] = []
        self.outports: List[Port] = []

    def __str__(self) -> str:
        raise NotImplementedError()

    def to_ma(self) -> str:
        raise NotImplementedError()

    def to_dict(self) -> dict:
        raise NotImplementedError()

    def add_outport(self, name: str):
        outport = OutPort(name, self)
        self.outports.append(outport)
        return self

    def add_inport(self, name: str):
        inport = InPort(name, self)
        self.inports.append(inport)
        return self

    def get_port(self, name: str) -> Port:
        for port in self.inports + self.outports:
            if port.name == name:
                return port
        raise PortNotFoundException()


class Port:
    def __init__(self, name: str, owner: Model):
        # a type could be added in the future as an extra checks
        self.name = name
        self.owner = owner

    def __str__(self):
        return self.name

    def get_identifier_for(self, model: Model) -> str:
        return self.name if model == self.owner else f"{self.name}@{self.owner.name}"

    def to_dict(self):
        return {
            'name': self.name,
            'message_type': 'Any'
        }


class InPort(Port):
    def to_dict(self):
        dic = super().to_dict()
        dic['kind'] = 'in'
        return dic


class OutPort(Port):
    def to_dict(self):
        dic = super().to_dict()
        dic['kind'] = 'out'
        return dic


class Link:
    def __init__(self, from_port: Port, to_port: Port):
        self.from_port = from_port
        self.to_port = to_port


class ExtInputLink(Link):
    def __init__(self, from_port: InPort, to_port: InPort):
        super().__init__(from_port, to_port)


class ExtOutputLink(Link):
    def __init__(self, from_port: OutPort, to_port: OutPort):
        super().__init__(from_port, to_port)


class IntLink(Link):
    def __init__(self, from_port: OutPort, to_port: InPort):
        super().__init__(from_port, to_port)


class Atomic(Model):
    def __init__(self, name: str, **model_params: str):
        super().__init__(name)
        self.model_params = model_params

    def __str__(self) -> str:
        return f"{self.name}@{self.get_abstract_model_name()}"

    def to_ma(self) -> str:
        ma = f"[{self.name}]\n"
        for param, value in self.model_params.items():
            ma += f"{param}: {value}\n"
        return ma

    def to_dict(self) -> dict:
        return {
            'id': self.name,
            'type': 'atomic',
            'ports': {
                'out': [outport.to_dict() for outport in self.outports],
                'in': [inport.to_dict() for inport in self.inports]
            }
        }

    def get_abstract_model_name(self) -> str:
        return type(self).__name__


class Coupled(Model):
    def __init__(self, name: str, subcomponents: List[Model]):
        super().__init__(name)
        self.subcomponents = subcomponents
        self.eic: List[ExtInputLink] = []
        self.eoc: List[ExtOutputLink] = []
        self.ic: List[IntLink] = []

    def __str__(self) -> str:
        return self.name

    def add_internal_coupling(self, link: IntLink):
        self.ic.append(link)

    def add_external_input_coupling(self, link: ExtInputLink):
        self.eic.append(link)

    def add_external_output_coupling(self, link: ExtOutputLink):
        self.eoc.append(link)

    # Implements Coupled functional interface
    def add_coupling(self, from_port: Union[Port, str], to_port: Union[Port, str]) -> Coupled:
        actual_from_port = None
        actual_to_port = None
        if isinstance(from_port, str):
            actual_from_port = self.get_port(from_port)
        elif isinstance(from_port, Port):
            actual_from_port = from_port

        if isinstance(to_port, str):
            actual_to_port = self.get_port(to_port)
        elif isinstance(to_port, Port):
            actual_to_port = to_port

        self.do_add_coupling(actual_from_port, actual_to_port)
        return self

    def do_add_coupling(self, from_port: Port, to_port: Port):
        # Internal coupling
        if isinstance(from_port, OutPort) and \
           isinstance(to_port, InPort):
            self.add_internal_coupling(IntLink(from_port, to_port))
        # External-Input
        elif isinstance(from_port, InPort) and \
                isinstance(to_port, InPort):
            self.add_external_input_coupling(ExtInputLink(from_port, to_port))
        # External-Output
        elif isinstance(from_port, OutPort) and \
                isinstance(to_port, OutPort):
            self.add_external_output_coupling(ExtOutputLink(from_port, to_port))
        else:
            raise Exception(
                f"This is not a valid coupling. Ports are {from_port.__class__}" +
                f" and {to_port.__class__}. Please check the provided ports.")

    def to_ma(self) -> str:
        ma = (
            f"[{self.name}]\n"
            f"components: {' '.join([str(c) for c in self.subcomponents])}\n"
            f"out: {' '.join([str(o) for o in self.outports])}\n"
            f"in: {' '.join([str(i) for i in self.inports])}\n"
        )
        links = cast(List[Link], self.eic) + cast(List[Link], self.ic) + cast(List[Link], self.eoc)
        for link in links:
            ma += f"link: {link.from_port.get_identifier_for(self)} "
            ma += f"{link.to_port.get_identifier_for(self)}\n"
        for model in self.subcomponents:
            ma += f"\n\n{model.to_ma()}"
        return ma

    def to_dict(self) -> dict:
        return {
            'id': self.name,
            'type': 'coupled',
            'models': [model.to_dict() for model in self.subcomponents],
            'ports': {
                'out': [outport.to_dict() for outport in self.outports],
                'in': [inport.to_dict() for inport in self.inports]
            },
            'eoc': [
                {
                    'to_port': coup.to_port.name,
                    'from_port': coup.from_port.name,
                    'from_model': coup.from_port.owner.name
                }
                for coup in self.eoc
            ],
            'eic': [
                {
                    'to_port': coup.to_port.name,
                    'to_model': coup.to_port.owner.name,
                    'from_port': coup.from_port.name
                }
                for coup in self.eic
            ],
            'ic': [
                {
                    'to_port': coup.to_port.name,
                    'to_model': coup.to_port.owner.name,
                    'from_port': coup.from_port.name,
                    'from_model': coup.from_port.owner.name
                }
                for coup in self.ic
            ]
        }
