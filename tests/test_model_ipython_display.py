import pytest
from unittest.mock import patch
import requests
import os
from pringles.models import Coupled
from .utils import make_queue_top_model_with_events


@pytest.fixture(autouse=True)
def _start_web_display_backend():
    with patch("pringles.backends.web_display._get_static_files_path")\
            as mock_get_static_files_path:
        mock_get_static_files_path.return_value = os.path.join(
            os.path.dirname(__file__), "resources/_test_statics")
        _start_server()
        yield


def test_simple_model_display():
    top, events = make_queue_top_model_with_events()
    top_html_representation = top._repr_html_()
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


def test_json_representation_is_embedded_raw_in_ipython_representation():
    from pringles.serializers import JsonSerializer
    queue_model, _ = make_queue_top_model_with_events()
    result = queue_model._repr_html_()
    assert JsonSerializer.serialize(queue_model) in result


def _start_server():
    tmp_coupled = Coupled("top", [])
    tmp_coupled._repr_html_()
