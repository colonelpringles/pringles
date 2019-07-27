import json

from IPython.display import IFrame  # pylint: disable=E0401
import urllib.parse

from colonel.models import Model
from colonel.serializers import JsonSerializer


class ModelDisplayOptions:
    def __init__(self, squared_models=False, show_message_type=True, show_port_name=True,
                 compress_in_left=False, sort_ports_by_name=True):
        self.squared_models = squared_models
        self.show_message_type = show_message_type
        self.show_port_name = show_port_name
        self.compress_in_left = compress_in_left
        self.sort_ports_by_name = sort_ports_by_name

    def as_json(self):
        return json.dumps({
            "squared_models": self.squared_models,
            "show_message_type": self.show_message_type,
            "show_port_name": self.show_port_name,
            "compress_in_left": self.compress_in_left,
            "sort_ports_by_name": self.sort_ports_by_name
        })


class ModelDisplay(IFrame):
    DIAGRAMMER_URL = 'https://colonelpringles.github.io/DEVSDiagrammer/basic.html'

    def __init__(self, model: Model, width='100%', height='600px', options=ModelDisplayOptions()):
        serialized_model = JsonSerializer.serialize(model)
        serialized_opt = options.as_json()
        url = urllib.parse.quote(f'{self.DIAGRAMMER_URL}?' +
                                 f'options={serialized_opt}&structure={serialized_model}',
                                 safe=':/?=&')
        super().__init__(url, width=width, height=height)
