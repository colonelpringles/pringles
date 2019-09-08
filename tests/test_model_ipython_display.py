import pytest
from unittest.mock import patch
from requests.models import Response
import os
from .utils import make_queue_top_model_with_events


class TestTimeoutRequester:
    def __init__(self, base_url, timeout):
        self.base_url = base_url
        self.timeout = timeout

    def get(self, uri: str) -> Response:
        import requests
        return requests.get(self.base_url + uri, timeout=self.timeout)


@pytest.fixture(autouse=True)
def _start_web_display_backend():
    with patch("pringles.backends.web_display._get_static_files_path")\
            as mock_get_static_files_path:
        mock_get_static_files_path.return_value = os.path.join(
            os.path.dirname(__file__), "resources/_test_statics")
        _start_server()
        yield


@pytest.fixture()
def test_requester() -> TestTimeoutRequester:
    from pringles.backends.web_display import WebApplication
    return TestTimeoutRequester(WebApplication.target_url, 10)


def test_simple_model_display(test_requester):
    top, events = make_queue_top_model_with_events()
    top_html_representation = top._repr_html_()
    print(top_html_representation)
    assert top.name in top_html_representation


def test_web_backed_is_alive(test_requester):
    response = test_requester.get("/heartbeat")
    assert response.text == "tutuc"


def test_static_is_served(test_requester):
    response = test_requester.get("/_static/static_test.txt")
    assert response.text == "holus"


def test_static_is_served_from_subfolder(test_requester):
    response = test_requester.get("/_static/test/static_test_2.txt")
    assert response.text == "holes"


def test_json_representation_is_embedded_raw_in_ipython_representation(test_requester):
    from pringles.serializers import JsonSerializer
    queue_model, _ = make_queue_top_model_with_events()
    result = queue_model._repr_html_()
    assert JsonSerializer.serialize(queue_model) in result


def _start_server():
    from pringles.models import Coupled
    tmp_coupled = Coupled("top", [])
    tmp_coupled._repr_html_()
