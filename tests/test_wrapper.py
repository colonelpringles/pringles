import unittest
from unittest import mock
import os
from colonel.wrapper.wrapper import Wrapper
from colonel.wrapper.errors import SimulatorExecutableNotFound

class WrapperTests(unittest.TestCase):

    def test_no_simulator_executable_found(self):
        with self.assertRaises(SimulatorExecutableNotFound):
            with mock.patch.dict(os.environ, {'PATH': ''}):
                wrapper = Wrapper()

    def test_simulator_executable_found_in_PATH(self):
        # Set current working directoy in path, so it discovers 'test_cd++'
        test_path_directory = os.path.dirname(os.path.abspath(__file__))
        with mock.patch.dict(os.environ, {'PATH': test_path_directory}):
            wrapper = Wrapper()