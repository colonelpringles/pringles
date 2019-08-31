import pytest
import requests
from pringles.models import Coupled
from .utils import make_queue_top_model_with_events


def test_simple_model_display():
    top, events = make_queue_top_model_with_events()
    top_html_representation = top._repr_html_().decode("utf-8")
    print(top_html_representation)
    assert top.name in top_html_representation


@pytest.mark.timeout(10)
def test_web_backed_is_alive():
    _start_server()
    response = requests.get("http://localhost:10982/test", timeout=10)
    assert response.text == "holis"


def _start_server():
    tmp_coupled = Coupled("top", [])
    tmp_coupled._repr_html_()
