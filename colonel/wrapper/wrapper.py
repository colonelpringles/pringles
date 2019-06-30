import os

from typing import Optional

from colonel.wrapper.errors import SimulatorExecutableNotFound


class ExecutableDiscoverer():
    def discover(self) -> Optional[str]:
        return self.do_discover()

    # Discoverer implementation
    def do_discover(self) -> Optional[str]:
        raise NotImplementedError()

    @staticmethod
    def is_executable_file(filepath: str) -> bool:
        return os.path.isfile(filepath) and os.access(filepath, os.X_OK)


class CompoundExecutableDiscoverer(ExecutableDiscoverer):
    def __init__(self, *discoverers: ExecutableDiscoverer):
        self.discoverers = discoverers

    def do_discover(self) -> Optional[str]:
        found_route = None
        for discoverer in self.discoverers:
            found_route = discoverer.discover()
            if found_route:
                return found_route
        return None


class PathEnvironmentVarExecutableDiscoverer(ExecutableDiscoverer):
    PATH_ENV_VAR = "PATH"

    def do_discover(self) -> Optional[str]:
        path = os.environ.get(PathEnvironmentVarExecutableDiscoverer.PATH_ENV_VAR, '')
        for directory in path.split(os.pathsep):
            executable_route = os.path.join(directory, Wrapper.CDPP_BIN)
            if ExecutableDiscoverer.is_executable_file(executable_route):
                return executable_route
        return None


class LibraryEnvironmentVarExecutableDiscoverer(ExecutableDiscoverer):
    def do_discover(self):
        try:
            cdpp_bin_directory = os.environ.get(Wrapper.CDPP_EXECUTABLE_ENV_VAR)
            if cdpp_bin_directory is not None:
                executable_route = os.path.join(cdpp_bin_directory, Wrapper.CDPP_BIN)
                if ExecutableDiscoverer.is_executable_file(executable_route):
                    return executable_route
        except KeyError:
            pass
        return None


class LibraryDefinedDirectoryExecutableDiscoverer(ExecutableDiscoverer):
    def do_discover(self):
        executable_route = os.path.join(Wrapper.CDPP_LIBRARY_DEFINED_EXECUTABLE_PATH,
                                        Wrapper.CDPP_BIN)
        if ExecutableDiscoverer.is_executable_file(executable_route):
            return executable_route
        return None


class Wrapper:
    CDPP_BIN = 'cd++'
    CDPP_EXECUTABLE_ENV_VAR = 'CDPP_BIN'
    CDPP_LIBRARY_DEFINED_EXECUTABLE_PATH = '../../'

    DRAWLOG_BIN = 'drawlog'
    simulationAbortedErrorMessage = 'Aborting simulation...\n'

    def __init__(self):
        self.executable_route = self.discover_executable_route()

    def discover_executable_route(self):
        discoverer = CompoundExecutableDiscoverer(
            PathEnvironmentVarExecutableDiscoverer(),
            LibraryEnvironmentVarExecutableDiscoverer(),
            LibraryDefinedDirectoryExecutableDiscoverer(),
        )
        found_route = discoverer.discover()
        if found_route is None:
            raise SimulatorExecutableNotFound()
        return found_route
