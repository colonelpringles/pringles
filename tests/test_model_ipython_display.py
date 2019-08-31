import pytest
import requests
from pringles.models import Coupled
from .utils import make_queue_top_model_with_events


@pytest.fixture(autouse=True)
def _start_web_display_backend():
    _start_server()
    yield


def test_simple_model_display():
    top, events = make_queue_top_model_with_events()
    top_html_representation = top._repr_html_().decode("utf-8")
    print(top_html_representation)
    assert top.name in top_html_representation


def test_web_backed_is_alive():
    response = requests.get("http://localhost:10982/test", timeout=10)
    assert response.text == "holis"


def test_static_is_served():
    response = requests.get("http://localhost:10982/_static/static_test.txt", timeout=10)
    assert response.text == "holus"


def test_static_is_served_from_subfolder():
    response = requests.get("http://localhost:10982/_static/test/static_test_2.txt", timeout=10)
    assert response.text == "holes"


def _start_server():
    tmp_coupled = Coupled("top", [])
    tmp_coupled._repr_html_()
