from typing import List, cast


class Model:
    def __init__(self, name: str):
        self.name = name
        self.inports: List[InPort] = []
        self.outports: List[OutPort] = []

    def __str__(self) -> str:
        raise NotImplementedError()

    def to_ma(self) -> str:
        raise NotImplementedError()

    def add_outport(self, name: str):
        outport = OutPort(name, self)
        self.outports.append(outport)
        return outport

    def add_inport(self, name: str):
        inport = InPort(name, self)
        self.inports.append(inport)
        return inport


class Port:
    def __init__(self, name: str, owner: Model):
        # a type could be added in the future as an extra checks
        self.name = name
        self.owner = owner

    def __str__(self):
        return self.name

    def get_identifier_for(self, model: Model) -> str:
        return self.name if model == self.owner else f"{self.name}@{self.owner.name}"


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

    def add_coupling(self, from_port: Port, to_port: Port):
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
            raise Exception("This is not a valid coupling. Please check the provided ports.")

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