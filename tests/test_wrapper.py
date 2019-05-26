import pytest
from colonel.wrapper.wrapper import Wrapper
from colonel.wrapper.errors import SimulatorExecutableNotFound

def test_no_simulator_executable_found():
    with pytest.raises(SimulatorExecutableNotFound):
        wrapper = Wrapper()