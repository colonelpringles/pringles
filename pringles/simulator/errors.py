class SimulatorExecutableNotFound(Exception):
    pass


class DuplicatedAtomicException(Exception):
    def __init__(self, name):
        super().__init__(f"Atomic named {name} has duplicated metadata.")


class AttributeIsImmutableException(AttributeError):
    pass
