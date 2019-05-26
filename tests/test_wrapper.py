import pytest
from unittest import mock
import os
from colonel.wrapper.wrapper import Wrapper
from colonel.wrapper.errors import SimulatorExecutableNotFound


TEST_PATH_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

def test_no_simulator_executable_found():
    with pytest.raises(SimulatorExecutableNotFound):
        with mock.patch.dict(os.environ, {'PATH': ''}):
            wrapper = Wrapper()

def test_simulator_executable_found_in_PATH():
    # Set current working directory in path, so it discovers 'cd++' in tests/
    with mock.patch.dict(os.environ, {'PATH': TEST_PATH_DIRECTORY}):
        wrapper = Wrapper()

def test_simulator_executable_found_in_library_env_var():
    with mock.patch.dict(os.environ, {'PATH':'', Wrapper.CDPP_EXECUTABLE_ENV_VAR: TEST_PATH_DIRECTORY}):
        wrapper = Wrapper()