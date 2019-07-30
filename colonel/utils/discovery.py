from typing import Union, List
from pyparsing import Word, Literal, alphanums, ParseException, delimitedList, ParserElement
from colonel.models import InPort, OutPort, Port
from io import StringIO  # File typing


class MetadataParsingException(Exception):
    pass


class AtomicMetadata:
    def __init__(self, name: str, input_ports: List[str], output_ports: List[str]):
        self.name = name
        self.input_ports = input_ports
        self.output_ports = output_ports


class AtomicMetadataExtractor:
    """Extractor from ports metadata from Atomcis cpp file.

    This should be improved to a more richer metadata, such as:
    ```
    @ModelMetadata
    name: some_name
    input_ports: port1, port2, port3
    output_ports: oport1, oport2
    ```
    """

    def __init__(self, source: Union[str, StringIO]):
        if isinstance(source, str):
            self.source = source
        else:
            self.source = source.read()

        port_names_list = delimitedList(Word(alphanums))
        metadata_start_keyword = Literal("@ModelMetadata")
        self.parser: ParserElement = metadata_start_keyword +\
            Literal("name:") +\
            Word(alphanums).setResultsName("model_name") +\
            Literal("input_ports:") +\
            port_names_list.setResultsName("input_ports") +\
            Literal("output_ports:") +\
            port_names_list.setResultsName("output_ports")

    def extract(self) -> AtomicMetadata:
        try:
            parse_results = self.parser.parseString(self.source)
            return AtomicMetadata(
                parse_results["model_name"],
                parse_results["input_ports"].asList(),
                parse_results["output_ports"].asList())
        except ParseException as pe:
            raise MetadataParsingException(pe)
