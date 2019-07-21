import pytest
import os
from colonel.wrapper.wrapper import Wrapper
from colonel.wrapper.config import CDPP_BIN_PATH
from colonel.wrapper.errors import SimulatorExecutableNotFound


TEST_PATH_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
TEST_EXECUTABLE = os.path.join(TEST_PATH_DIRECTORY, Wrapper.CDPP_BIN)
CDPP_BIN_EXECUTABLE_PATH = os.path.join(CDPP_BIN_PATH, Wrapper.CDPP_BIN)


def test_simulator_executable_found_in_library_defined_dir():
    wrapper = Wrapper()
    assert wrapper.executable_route == CDPP_BIN_EXECUTABLE_PATH
