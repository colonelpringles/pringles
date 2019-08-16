import pytest  # noqa
from pringles.models import InPort, OutPort
from pringles.simulator import Simulator


def test_extract_metadata_and_instantiate_is_coherent():
    simulator = Simulator("aBinPath", "tests/resources/")
    assert simulator.get_registry().Queue is not None

    awesome_queue = simulator.get_registry().Queue("awesome")
    assert awesome_queue.get_port("in") is not None
    assert awesome_queue.get_port("done") is not None
    assert awesome_queue.get_port("out") is not None
    assert isinstance(awesome_queue.get_port("in"), InPort)
    assert isinstance(awesome_queue.get_port("done"), InPort)
    assert isinstance(awesome_queue.get_port("out"), OutPort)
