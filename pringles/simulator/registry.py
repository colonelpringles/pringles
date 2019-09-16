import os
from typing import Optional, List, Type

from pringles.models import Atomic, AtomicModelBuilder
from pringles.simulator.errors import DuplicatedAtomicException
from pringles.utils import AtomicMetadataExtractor
from pringles.utils.errors import MetadataParsingException, NonExistingAtomicClassException


class AtomicRegistry:
    """A registry where all Atomic model classes are registered into. Usually, this atomics are
    discovered and populated with the metadata way.
    """

    SUPPORTED_FILE_EXTENSIONS = [".cpp", ".hpp", ".h"]

    def __init__(self, user_models_dir: Optional[str] = None, autodiscover: bool = True):
        self.user_models_dir = user_models_dir
        self.discovered_atomics: List[Type[Atomic]] = []
        if autodiscover and user_models_dir is not None:
            self._discover_atomics()

    def _add_atomic_class_as_attribute(self, name: str, atomic_class: Type[Atomic]):
        if hasattr(self, name):
            raise DuplicatedAtomicException(name)
        setattr(self, name, atomic_class)

    def get_by_name(self, name: str) -> type:
        """Retrieves an Atomic class from the registry, by class name. Similar to getattr.

        :param name: The atomic class name
        :type name: str
        :raises NonExistingAtomicClassException: The atomic looked for is not present in the
            registry
        :return: The atomic class named as the parameter
        :rtype: type
        """
        try:
            return getattr(self, name)
        except AttributeError:
            raise NonExistingAtomicClassException(
                f'Atomic class named {name} is not present in the registry.')

    def _discover_atomics(self) -> None:
        assert self.user_models_dir is not None

        files_to_extract_from = []
        for filename in os.listdir(self.user_models_dir):
            filename_with_path = os.path.join(self.user_models_dir, filename)
            if os.path.isfile(filename_with_path):
                _, file_extension = os.path.splitext(filename)
                if file_extension in AtomicRegistry.SUPPORTED_FILE_EXTENSIONS:
                    files_to_extract_from.append(filename_with_path)

        # extract metadata from discovered source files
        for discovered_path in files_to_extract_from:
            with open(discovered_path, "r") as discovered_file:
                try:
                    discovered_metadata = AtomicMetadataExtractor(discovered_file).extract()
                except MetadataParsingException:
                    pass
                else:
                    atomic_class_builder = AtomicModelBuilder().with_name(discovered_metadata.name)
                    for name in discovered_metadata.input_ports:
                        atomic_class_builder.with_input_port(name)
                    for name in discovered_metadata.output_ports:
                        atomic_class_builder.with_output_port(name)
                    built_class = atomic_class_builder.build()
                    self._add_atomic_class_as_attribute(discovered_metadata.name,
                                                        built_class)
                    self.discovered_atomics.append(built_class)
