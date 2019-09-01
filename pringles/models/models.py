"""
This is the models module docstring
"""
from __future__ import annotations
from typing import List, Any, Union

DISCOVERED_INPUT_PORTS_FIELD = "discovered_input_ports"
DISCOVERED_OUTPUT_PORTS_FIELD = "discovered_output_ports"


class PortNotFoundException(Exception):
    pass


class AtomicModelBuilder:
    """
    Atomic models class builder.
    """

    def __init__(self):
        self.discovered_input_ports_fields = []
        self.discovered_output_ports_fields = []

    def with_name(self, name: str) -> AtomicModelBuilder:
        self.name = name
        return self

    def with_input_port(self, name: str) -> AtomicModelBuilder:
        self.discovered_input_ports_fields.append(name)
        return self

    def with_output_port(self, name: str) -> AtomicModelBuilder:
        self.discovered_output_ports_fields.append(name)
        return self

    def build(self) -> Any:
        return type(self.name, (Atomic,), {
            DISCOVERED_INPUT_PORTS_FIELD: self.discovered_input_ports_fields,
            DISCOVERED_OUTPUT_PORTS_FIELD: self.discovered_output_ports_fields
        })


class Model:
    """
    Model is the base class for all DEVS model instances, be it an Atomic or a Coupled.
    """

    def __init__(self, name: str):
        self.name = name
        self.inports: List[Port] = []
        self.outports: List[Port] = []

    def __str__(self) -> str:
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
        raise PortNotFoundException(name)


class Port:
    """
    Port is the base class for all DEVS ports.
    """

    def __init__(self, name: str, owner: Model):
        # a type could be added in the future as an extra checks
        self.name = name
        self.owner = owner

    def __str__(self):
        return self.name

    def get_identifier_for(self, model: Model) -> str:
        return self.name if model == self.owner else f"{self.name}@{self.owner.name}"


class InPort(Port):
    """Input port.
    """
    pass


class OutPort(Port):
    """Output port.
    """
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

        if hasattr(self, DISCOVERED_INPUT_PORTS_FIELD):
            for input_port_name in getattr(self, DISCOVERED_INPUT_PORTS_FIELD):
                self.add_inport(input_port_name)
        if hasattr(self, DISCOVERED_OUTPUT_PORTS_FIELD):
            for output_port_name in getattr(self, DISCOVERED_OUTPUT_PORTS_FIELD):
                self.add_outport(output_port_name)

    def __str__(self) -> str:
        return f"{self.name}@{self.get_abstract_model_name()}"

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

    # Method used by ipython to html-display a model
    def _repr_html_(self) -> str:
        from pringles.backends import ipython_inline_display
        return ipython_inline_display(self).decode("utf-8")
