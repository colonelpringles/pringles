import subprocess
from subprocess import CalledProcessError
import os
from .errors import *
from typing import List

# sample cd++ command
# cd++ -m2Voronoi.ma -ooutput -t00:01:00:00 -llogs

# sample drawlog command
# drawlog -m2Voronoi.ma -i00:00:00:100 -cvoronoiExpansion -llogs -z/tmp/altoPerro.npz

class SimulationNotExectutedException(Exception):
    pass

class SimulationProcessFailedException(CalledProcessError):
    pass

class SimulationExecutedButFailedException(Exception):
    pass

# Common interface
class ExecutableDiscoverer():
    def __init__(self):
        pass

    def discover(self) -> str:
        return self.do_discover()

    # Discoverer implementation
    def do_discover(self) -> str:
        raise NotImplementedError()
    
    @staticmethod
    def is_executable_file(filepath : str) -> bool:
        return os.path.isfile(filepath) and os.access(filepath, os.X_OK)

class CompoundExecutableDiscoverer(ExecutableDiscoverer):
    def __init__(self, *discoverers : List[ExecutableDiscoverer]):
        self.discoverers = discoverers

    def do_discover(self) -> str:
        found_route = None
        for discoverer in self.discoverers:
            found_route = discoverer.discover()
            if found_route:
                return found_route
        return None

class PathEnvironmentVarExecutableDiscoverer(ExecutableDiscoverer):
    PATH_ENV_VAR = "PATH"
    def do_discover(self) -> str:
        for path in os.environ.get(PathEnvironmentVarExecutableDiscoverer.PATH_ENV_VAR).split(os.pathsep):
            executable_route = os.path.join(path, Wrapper.CDPP_BIN)
            if ExecutableDiscoverer.is_executable_file(executable_route):
                return executable_route
        return None

class LibraryEnvironmentVarExecutableDiscoverer(ExecutableDiscoverer):
    def do_discover(self):
        try:
            cdpp_bin_directory = os.environ.get(Wrapper.CDPP_EXECUTABLE_ENV_VAR)
            if cdpp_bin_directory != None:
                executable_route = os.path.join(cdpp_bin_directory, Wrapper.CDPP_BIN)
                if ExecutableDiscoverer.is_executable_file(executable_route):
                    return executable_route
        except KeyError as e:
            pass
        return None

class Wrapper:
    CDPP_BIN = 'cd++'
    CDPP_EXECUTABLE_ENV_VAR = 'CDPP_BIN'
    CDPP_LIBRARY_DEFINED_EXECUTABLE_PATH = '~/Facultad/pringles/cdpp_kernel/bin/'

    DRAWLOG_BIN = 'drawlog'
    simulationAbortedErrorMessage = 'Aborting simulation...\n'

    def __init__(self):
        self.executable_route = self.discover_executable_route()

    def discover_executable_route(self):
        discoverer = CompoundExecutableDiscoverer(\
            PathEnvironmentVarExecutableDiscoverer(),\
            LibraryEnvironmentVarExecutableDiscoverer()\
            )
        found_route = discoverer.discover()        
        if found_route == None:
            raise SimulatorExecutableNotFound()
        return found_route

    def run(self):
        simulationArguments = self.getArguments()
        try:
            self.simulationProcessData = subprocess.run(simulationArguments, capture_output=True, check=True)

        except CalledProcessError as e:
            # The exception contains information about the failed simulation process
            raise SimulationProcessFailedException(e.returncode, e.cmd, e.output, e.stderr)
        if self.getSimulationStdOut().endswith(self.__class__.simulationAbortedErrorMessage):
            raise SimulationExecutedButFailedException()

        # TODO: Add check on 'Aborting simulation...' stdout last line, and throw error

    def getSimulationStdOut(self):
        return self.simulationProcessData.stdout.decode('ascii')

    def getSimulationOutput(self):
        return 'STDOUT:\n' + self.getSimulationStdOut() + '\nSTDERR:\n' + self.simulationProcessData.stderr.decode('ascii')
    
    def getLogsPath(self):
        if not self.simulationWasExecuted():
            raise SimulationNotExectutedException()
        return self.logsFileName

    def getOutputPath(self):
        if not self.simulationWasExecuted():
            raise SimulationNotExectutedException()
        return self.outputFileName

    def simulationWasExecuted(self):
        return self.simulationProcessData is not None

    def getArguments(self):
        self.generateOutfilesPaths()
        arguments = [self.Wrapper.CDPP_BIN, f'-m{self.model.get_path()}',\
            f'-o{self.outputFileName}', f'-t{self.endTime}', f'-l{self.logsFileName}']
        return arguments

    def generateOutfilesPaths(self):
        pass