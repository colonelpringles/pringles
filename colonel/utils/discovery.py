from typing import Union, List
from colonel.models import InPort, OutPort, Port
from io import StringIO  # File typing


class AtomicMetadataExtractor:
    """Extractor from ports metadata from Atomcis cpp file."""
    def __init__(self, source: Union[str, StringIO]):
        if isinstance(source, str):
            self.source = source
        else:
            self.source = source.read()

    def extract_ports(self) -> List[Port]:
        return []
