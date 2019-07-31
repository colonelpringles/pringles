from typing import Union, List
from pyparsing import Word, Literal, alphanums, ParseException, delimitedList, ParserElement, Optional
from colonel.models import InPort, OutPort, Port
from io import StringIO  # File typing
import re


class MetadataParsingException(Exception):
    pass


class AtomicMetadata:
    def __init__(self, name: str, input_ports: List[str], output_ports: List[str]):
        self.name = name
        self.input_ports = input_ports
        self.output_ports = output_ports

    def __eq__(self, other):
        if not isinstance(other, AtomicMetadata):
            return False
        return self.name == other.name and\
            self.input_ports == other.input_ports and\
            self.output_ports == other.output_ports


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

    CPP_MULTILINE_COMMENT_RE = "/\*(.*)\*/"

    def __init__(self, source: Union[str, StringIO]):
        self.source = source
        self._initialize_parser()

    def _initialize_parser(self):
        port_names_list = delimitedList(Word(alphanums))
        metadata_start_keyword = Literal("@ModelMetadata")
        self.parser: ParserElement = metadata_start_keyword +\
            Literal("name:") +\
            Word(alphanums).setResultsName("model_name") +\
            Optional(
                Literal("input_ports:") +
                port_names_list.setResultsName("input_ports")
            ) +\
            Optional(
                Literal("output_ports:") +
                port_names_list.setResultsName("output_ports")
            )

    def _do_extract_from_file(self, file_source: StringIO) -> AtomicMetadata:
        matched_multiline_comments = re.findall(
            AtomicMetadataExtractor.CPP_MULTILINE_COMMENT_RE, file_source.read(), re.DOTALL)
        for index, matched_comment in enumerate(matched_multiline_comments):
            try:
                return self._do_extract_from_string(matched_comment)
            except ParseException as pe:
                if index == len(matched_multiline_comments) - 1:
                    # Should fail if metadata not found here
                    raise MetadataParsingException(pe)

    def _do_extract_from_string(self, string_source: str) -> AtomicMetadata:
        try:
            parse_results = self.parser.parseString(string_source)
            try:
                parsed_input_ports = parse_results["input_ports"].asList()
            except KeyError:
                parsed_input_ports = []
            try:
                parsed_output_ports = parse_results["output_ports"].asList()
            except KeyError:
                parsed_output_ports = []
            return AtomicMetadata(
                parse_results["model_name"],
                parsed_input_ports,
                parsed_output_ports)
        except ParseException as pe:
            raise MetadataParsingException(pe)

    def extract(self) -> AtomicMetadata:
        if isinstance(self.source, str):
            return self._do_extract_from_string(self.source)
        else:
            return self._do_extract_from_file(self.source)


class CppCommentsLexer:
    def __init__(self, source: str):
        self.source = source

    def lex(self) -> List[str]:
        return []