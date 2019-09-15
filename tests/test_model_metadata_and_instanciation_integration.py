import pytest  # noqa
import os
from pringles.models import InPort, OutPort
from pringles.utils.errors import NonExistingAtomicClassException
from pringles.simulator import Simulator


CDPP_BIN_PATH = os.path.join(os.path.dirname(__file__), '../cdpp/src/bin/')


@pytest.fixture
def simulator_with_rocket_on_registry():
    simulator = Simulator(CDPP_BIN_PATH, "tests/resources/")
    yield simulator
    import pringles.models.models as pringles_models_module
    del pringles_models_module.Rocket


def test_extract_metadata_and_instantiate_is_coherent(simulator_with_rocket_on_registry):
    assert simulator_with_rocket_on_registry.get_registry().Rocket is not None

    awesome_queue = simulator_with_rocket_on_registry.get_registry().Rocket("awesome")
    assert awesome_queue.get_port("in") is not None
    assert awesome_queue.get_port("done") is not None
    assert awesome_queue.get_port("out") is not None
    assert isinstance(awesome_queue.get_port("in"), InPort)
    assert isinstance(awesome_queue.get_port("done"), InPort)
    assert isinstance(awesome_queue.get_port("out"), OutPort)


def test_registry_get_by_name_method(simulator_with_rocket_on_registry):
    registry = simulator_with_rocket_on_registry.get_registry()
    assert registry.Rocket == registry.get_by_name("Rocket")


def test_registry_get_by_name_non_existing_atomic(simulator_with_rocket_on_registry):
    registry = simulator_with_rocket_on_registry.get_registry()
    with pytest.raises(NonExistingAtomicClassException):
        registry.get_by_name("Falopa")
