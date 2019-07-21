from typing import Sequence


class Port:
    def __init__(self, name: str):
        # a type could be added in the future as an extra checks
        self.name = name


class InPort(Port):
    pass


class OutPort(Port):
    pass


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


class Model:
    pass


class Atomic(Model):
    def __init__(self, name: str, inports: Sequence[InPort], outports: Sequence[OutPort]):
        self.name = name
        self.inports = inports
        self.outports = outports


class Coupled(Model):
    def __init__(self, subcomponents: Sequence[Model],
                 inports: Sequence[InPort], outports: Sequence[OutPort],
                 eic: Sequence[ExtInputLink], eoc: Sequence[ExtOutputLink],
                 ic: Sequence[IntLink]):
        self.subcomponents = subcomponents
        self.inports = inports
        self.outports = outports
        self.eic = eic
        self.eoc = eoc
        self.ic = ic
