import pytest
from unittest import mock
import os
from colonel.wrapper.wrapper import Wrapper
from colonel.wrapper.errors import SimulatorExecutableNotFound

def test_no_simulator_executable_found():
    with pytest.raises(SimulatorExecutableNotFound):
        with mock.patch.dict(os.environ, {'PATH': ''}):
            wrapper = Wrapper()

def test_simulator_executable_found_in_PATH():
    # Set current working directory in path, so it discovers 'cd++' in tests/
    test_path_directory = os.path.dirname(os.path.abspath(__file__))
    with mock.patch.dict(os.environ, {'PATH': test_path_directory}):
        wrapper = Wrapper()