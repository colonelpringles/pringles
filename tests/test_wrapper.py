import pytest
from unittest import mock
import os
from colonel.wrapper.wrapper import Wrapper
from colonel.wrapper.config import CDPP_BIN_PATH
from colonel.wrapper.errors import SimulatorExecutableNotFound


TEST_PATH_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
TEST_EXECUTABLE = os.path.join(TEST_PATH_DIRECTORY, Wrapper.CDPP_BIN)
CDPP_BIN_EXECUTABLE_PATH = os.path.join(CDPP_BIN_PATH, Wrapper.CDPP_BIN)


@pytest.mark.skip(reason = "Deprecated executable locator")
@mock.patch.dict(os.environ, {'PATH': ''})
def test_no_simulator_executable_found():
    with pytest.raises(SimulatorExecutableNotFound):
        wrapper = Wrapper()  # noqa: F841


@pytest.mark.skip(reason = "Deprecated executable locator")
@mock.patch.dict(os.environ, {'PATH': TEST_PATH_DIRECTORY})
def test_simulator_executable_found_in_PATH():
    # Set current working directory in path, so it discovers 'cd++' in tests/
    wrapper = Wrapper()
    assert wrapper.executable_route == TEST_EXECUTABLE


@pytest.mark.skip(reason = "Deprecated executable locator")
@mock.patch.dict(os.environ, {'PATH': '', Wrapper.CDPP_EXECUTABLE_ENV_VAR: TEST_PATH_DIRECTORY})
def test_simulator_executable_found_in_library_env_var():
    wrapper = Wrapper()
    assert wrapper.executable_route == TEST_EXECUTABLE


def test_simulator_executable_found_in_library_defined_dir():
    wrapper = Wrapper()
    assert wrapper.executable_route == CDPP_BIN_EXECUTABLE_PATH