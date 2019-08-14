from typing import List, TextIO
from pyparsing import (Word, Literal, alphanums, ParseException,
                       delimitedList, ParserElement, Optional)

from pringles.utils.errors import MetadataParsingException


class AtomicMetadata:
    """Metadata about a atomic model.
    """

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

    def __init__(self, source: TextIO):
        """Main constructor

        :param source: a C++ containing the model metadata in a multi-line comment
        :type source: File
        """
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

    def _do_extract_from_file(self, file_source: TextIO) -> AtomicMetadata:
        lexed_comments = CppCommentsLexer(file_source.read()).lex()
        for index, matched_comment in enumerate(lexed_comments):
            try:
                return self._do_extract_from_string(matched_comment)
            except MetadataParsingException as pe:
                if index == len(lexed_comments) - 1:
                    # Should fail if metadata not found here
                    raise MetadataParsingException(pe)
        raise MetadataParsingException("No metadata found")

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
        """Extract the model metadata from the C++ source file."""
        return self._do_extract_from_file(self.source)


class CppCommentsLexer:
    _COMMENTS_START_TOKEN = "/*"
    _COMMENTS_END_TOKEN = "*/"

    def __init__(self, source: str):
        self.source = source
        self._index = 0
        self._size = len(source)
        self._pushed_symbols = ""
        self._lexed_comments: List[str] = []

    def _peek(self, n=1):
        return self.source[self._index: self._index + n]

    def _advance(self, n=1):
        self._index += n

    def lex(self) -> List[str]:
        while self._index + 3 < self._size:
            self._lex_till_inside_comment()
            self._lex_comment_pushing_symbols()
            self._push_lexed_comment()

        return self._lexed_comments

    def _lex_comment_pushing_symbols(self):
        self._pushed_symbols = ""  # clear pushed symbols
        while (self._index + 1 < self._size) and self._peek(2) !=\
                CppCommentsLexer._COMMENTS_END_TOKEN:
            self._pushed_symbols += self._peek()
            self._advance(1)  # go to next symbol
        self._advance(2)  # skip end comment symbol
        # now outside comment, with contents in self._pushed_symbols

    def _push_lexed_comment(self):
        self._lexed_comments.append(self._pushed_symbols)

    def _lex_till_inside_comment(self):
        while (self._index + 1 < self._size) and self._peek(2) !=\
                CppCommentsLexer._COMMENTS_START_TOKEN:
            self._advance(1)  # go to next symbol
        self._advance(2)  # skip start comment token
