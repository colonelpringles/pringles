from typing import Sequence


class Model:
    def to_ma(self) -> str:
        raise NotImplementedError()

    def __str__(self) -> str:
        raise NotImplementedError()


class Port:
    def __init__(self, name: str, owner: Model):
        # a type could be added in the future as an extra checks
        self.name = name
        self.owner = owner

    def __str__(self):
        return self.name


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


class Atomic(Model):
    def __init__(self, name: str, inports: Sequence[InPort],
                 outports: Sequence[OutPort], **model_params: str):
        self.name = name
        self.inports = inports
        self.outports = outports
        self.model_params = model_params

    def __str__(self) -> str:
        return f"{self.name}@{self.get_abstract_model_name()}"

    def to_ma(self) -> str:
        ma = f"[{self.name}]\n"
        for param, value in self.model_params.items():
            ma += f"{param}: {value}\n"
        return ma

    def get_abstract_model_name(self) -> str:
        return type(self).__name__


class Coupled(Model):
    def __init__(self, name: str, subcomponents: Sequence[Model],
                 inports: Sequence[InPort], outports: Sequence[OutPort],
                 eic: Sequence[ExtInputLink], eoc: Sequence[ExtOutputLink],
                 ic: Sequence[IntLink]):
        self.name = name
        self.subcomponents = subcomponents
        self.inports = inports
        self.outports = outports
        self.eic = eic
        self.eoc = eoc
        self.ic = ic

    def __str__(self) -> str:
        return self.name

    def to_ma(self) -> str:
        ma = (
            f"[{self.name}]\n"
            f"components: {' '.join([str(c) for c in self.subcomponents])}\n"
            f"out: {' '.join([str(o) for o in self.outports])}\n"
            f"in: {' '.join([str(i) for i in self.inports])}\n"
        )
        for link in self.eic:
            ma += f"link: {link.from_port} {self.to_port}\n"
        return ma        
