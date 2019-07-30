import pytest
from colonel.utils.discovery import AtomicMetadataExtractor
from colonel.models import InPort, OutPort


def test_no_port_metadata_does_not_fail():
    source = "void main(char** argv) {\n\tprintf(\"\");\n}"
    assert AtomicMetadataExtractor(source).extract_ports() == []

def test_single_input_port_extracted_correctly():
    source = "@InputPort(in)"
    assert AtomicMetadataExtractor(source).extract_ports() == [InPort("in", None)]


def test_single_output_port_extracted_correctly():
    source = "@OutputPort(out)"
    assert AtomicMetadataExtractor(source).extract_ports() == [OutPort("out", None)]


def test_multiple_ports_are_extracted_correctly():
    source = "@OutputPort(out)\n@InputPort(perro1)\n@InputPort(gato)"
    assert AtomicMetadataExtractor(source).extract_ports() == [OutPort("out", None),
                                                               InPort("perro1", None),
                                                               InPort("gato", None)]
