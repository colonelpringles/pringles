import pytest
from colonel.utils.discovery import AtomicMetadataExtractor
from colonel.models import InPort, OutPort


def test_single_input_port_extracted_correctly():
    source = "@InputPort(in)"
    assert AtomicMetadataExtractor(source).extract_ports() == [InPort("in", None)]

def test_single_output_port_extracted_correctly():
    source = "@OutputPort(out)"
    assert AtomicMetadataExtractor(source).extract_ports() == [OutPort("out", None)]