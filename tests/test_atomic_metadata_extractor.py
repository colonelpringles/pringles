import pytest  # noqa
from pringles.utils.errors import MetadataParsingException
from pringles.utils.discovery import (AtomicMetadataExtractor,
                                      AtomicMetadata)


# Helper to hide the private method call
def extract_metadata_from_string(source: str):
    return AtomicMetadataExtractor(source)._do_extract_from_string(source)


def test_no_metadata_fails():
    with pytest.raises(MetadataParsingException):
        source = "void main(char** argv) {\n\tprintf(\"\");\n}"
        extract_metadata_from_string(source)


def test_just_model_name_in_metadata():
    source = """
    @PringlesModelMetadata
    name:perro
    """
    assert extract_metadata_from_string(source) == AtomicMetadata("perro", [], [])


@pytest.mark.parametrize("name", [
    ("perro"),
    ("perro_loco"),
    ("perro-loco"),
    ("123perro-loco"),
    ("perro-LoCo_546")
])
def test_supported_model_names(name: str):
    source = """
    @PringlesModelMetadata
    name:%s
    """ % name
    assert extract_metadata_from_string(source) == AtomicMetadata(name, [], [])


def test_single_output_port_extracted_correctly():
    source = """
    @PringlesModelMetadata
    name:perro
    output_ports: perro, gato
    """
    assert extract_metadata_from_string(source) ==\
        AtomicMetadata("perro", [], ["perro", "gato"])


def test_multiple_ports_are_extracted_correctly():
    source = """
    @PringlesModelMetadata
    name:   perro
    input_ports: ornito, rinco
    output_ports: perro   , gato
    """
    assert extract_metadata_from_string(source) ==\
        AtomicMetadata("perro", ["ornito", "rinco"], ["perro", "gato"])


def test_model_cpp_file_with_metadata_is_parsed_correctly():
    with open("tests/resources/rocket_model.h", "r") as rocket_model_source_file:
        assert AtomicMetadataExtractor(rocket_model_source_file).extract() == \
            AtomicMetadata("Rocket", ["in", "done"], ["out"])
