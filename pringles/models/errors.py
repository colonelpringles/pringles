
class AtomicNameIsKeyWordException(Exception):
    def __init__(self, atomic_name):
        super().__init__(f"The name of your atomic ({atomic_name}) is a keyword.")
