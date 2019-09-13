import pytest  # noqa
import os
from pringles.models import InPort, OutPort
from pringles.simulator import Simulator


CDPP_BIN_PATH = os.path.join(os.path.dirname(__file__), '../cdpp/src/bin/')


def test_extract_metadata_and_instantiate_is_coherent():
    simulator = Simulator(CDPP_BIN_PATH, "tests/resources/")
    assert simulator.get_registry().Rocket is not None

    awesome_queue = simulator.get_registry().Rocket("awesome")
    assert awesome_queue.get_port("in") is not None
    assert awesome_queue.get_port("done") is not None
    assert awesome_queue.get_port("out") is not None
    assert isinstance(awesome_queue.get_port("in"), InPort)
    assert isinstance(awesome_queue.get_port("done"), InPort)
    assert isinstance(awesome_queue.get_port("out"), OutPort)
