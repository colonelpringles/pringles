from typing import Union, List
from pyparsing import Word, Literal, alphanums, ParserElement, ParseException
from colonel.models import InPort, OutPort, Port
from io import StringIO  # File typing


class AtomicMetadataExtractor:
    """Extractor from ports metadata from Atomcis cpp file."""

    def __init__(self, source: Union[str, StringIO]):
        if isinstance(source, str):
            self.source = source
        else:
            self.source = source.read()

        self.input_port_expression_parser: ParserElement = Literal(
            "@InputPort(").setResultsName("type") + Word(alphanums).setResultsName("name") +\
            Literal(")")
        self.output_port_expression_parser: ParserElement = Literal(
            "@OutputPort(").setResultsName("type") + Word(alphanums).setResultsName("name") +\
            Literal(")")

    def extract_ports(self) -> List[Port]:
        exctracted_ports = []
        for line in self.source.splitlines():
            try:
                input_port_result = self.input_port_expression_parser.parseString(line)
                port_name = input_port_result["name"]
                exctracted_ports.append(InPort(port_name, None))
            except ParseException:
                pass
            try:
                output_port_result = self.output_port_expression_parser.parseString(line)
                port_name = output_port_result["name"]
                exctracted_ports.append(OutPort(port_name, None))
            except ParseException:
                pass
        return exctracted_ports
