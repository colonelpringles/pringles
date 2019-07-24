import pytest
import os
from colonel.wrapper.wrapper import Wrapper
from colonel.wrapper.config import CDPP_BIN_PATH
from colonel.wrapper.errors import SimulatorExecutableNotFound
from colonel.models import Coupled, Atomic


TEST_PATH_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
TEST_EXECUTABLE = os.path.join(TEST_PATH_DIRECTORY, Wrapper.CDPP_BIN)
CDPP_BIN_EXECUTABLE_PATH = os.path.join(CDPP_BIN_PATH, Wrapper.CDPP_BIN)


class Queue(Atomic):
    pass


def test_simulator_executable_found_in_library_defined_dir():
    wrapper = Wrapper()
    assert wrapper.executable_route == CDPP_BIN_EXECUTABLE_PATH


def test():
    wrapper = Wrapper()

    sample_queue = Queue("sample_queue", preparation="0:0:0:1")
    queue_in = sample_queue.add_inport("in")
    queue_in_done = sample_queue.add_inport("done")
    queue_out = sample_queue.add_outport("out")
    top_model = Coupled("top", [sample_queue])
    incoming_event_port = top_model.add_inport("incoming_Event")
    done_event_port = top_model.add_inport("done_Event")
    emitted_signal_port = top_model.add_outport("emitted_signal")
    top_model.add_coupling(done_event_port, queue_in_done)
    top_model.add_coupling(queue_out, emitted_signal_port)
    top_model.add_coupling(incoming_event_port, queue_in)

    sim_result = wrapper.run_simulation(top_model,
                                        events_file="../pringles/test_models/simple_queue/test.ev")

    assert sim_result.successful()
