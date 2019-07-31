import pytest  # noqa
from colonel.utils.discovery import AtomicMetadataExtractor, MetadataParsingException, AtomicMetadata
from colonel.models import InPort, OutPort


def test_no_metadata_fails():
    with pytest.raises(MetadataParsingException):
        source = "void main(char** argv) {\n\tprintf(\"\");\n}"
        AtomicMetadataExtractor(source).extract()


def test_just_model_name_in_metadata():
    source = """
    @ModelMetadata
    name:perro
    """
    assert AtomicMetadataExtractor(source).extract() == AtomicMetadata("perro", [], [])


def test_single_output_port_extracted_correctly():
    source = """
    @ModelMetadata
    name:perro
    output_ports: perro, gato
    """
    assert AtomicMetadataExtractor(source).extract(
    ) == AtomicMetadata("perro", [], ["perro", "gato"])


def test_multiple_ports_are_extracted_correctly():
    source = """
    @ModelMetadata
    name:   perro
    input_ports: ornito, rinco
    output_ports: perro   , gato
    """
    assert AtomicMetadataExtractor(source).extract() == AtomicMetadata("perro",
                                                                       ["ornito", "rinco"],
                                                                       ["perro", "gato"])


def test_model_cpp_file_with_metadata_is_parsed_correctly():
    with open("tests/resources/queue.h", "r") as queue_source_file:
        assert AtomicMetadataExtractor(queue_source_file).extract() == \
                AtomicMetadata("Queue", ["in", "done"], ["out"])
