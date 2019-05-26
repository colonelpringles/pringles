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

    def discover(self) -> bool:
        return self.do_discover()

    # Discoverer implementation
    def do_discover(self) -> bool:
        raise NotImplementedError()
    
    @staticmethod
    def is_executable_file(filepath : str) -> bool:
        return os.path.isfile(filepath) and os.access(filepath, os.X_OK)

class CompoundExecutableDiscoverer(ExecutableDiscoverer):
    def __init__(self, *discoverers : List[ExecutableDiscoverer]):
        self.discoverers = discoverers

    def do_discover(self):
        found = False
        for discoverer in self.discoverers:
            found = discoverer.discover()
            if found:
                return True
        return False

class PathEnvironmentVarExecutableDiscoverer(ExecutableDiscoverer):
    PATH_ENV_VAR = "PATH"
    def do_discover(self) -> bool:
        for path in os.environ.get(PathEnvironmentVarExecutableDiscoverer.PATH_ENV_VAR).split(os.pathsep):
            executable_route = os.path.join(path, Wrapper.CDPP_BIN)
            if ExecutableDiscoverer.is_executable_file(executable_route):
                return True
        return False

class LibraryEnvironmentVarExecutableDiscoverer(ExecutableDiscoverer):
    def do_discover(self):
        try:
            cdpp_bin_directory = os.environ.get(Wrapper.CDPP_EXECUTABLE_ENV_VAR)
            if cdpp_bin_directory != None:
                executable_route = os.path.join(cdpp_bin_directory, Wrapper.CDPP_BIN)
                if ExecutableDiscoverer.is_executable_file(executable_route):
                    return True
        except KeyError as e:
            pass
        return False


class Wrapper:
    CDPP_BIN = 'cd++'
    CDPP_EXECUTABLE_ENV_VAR = 'CDPP_BIN'
    DRAWLOG_BIN = 'drawlog'
    simulationAbortedErrorMessage = 'Aborting simulation...\n'

    def __init__(self):
        discoverer = CompoundExecutableDiscoverer(\
            PathEnvironmentVarExecutableDiscoverer(),\
            LibraryEnvironmentVarExecutableDiscoverer()\
            )
        found = discoverer.discover()        
        if not found:
            raise SimulatorExecutableNotFound()

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