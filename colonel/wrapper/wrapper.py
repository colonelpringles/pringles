import subprocess
from subprocess import CalledProcessError
import os
from .errors import *

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

class Wrapper:
    CDPP_BIN = 'cd++'
    CDPP_EXECUTABLE_ENV_VAR = 'CDPP_BIN'
    DRAWLOG_BIN = 'drawlog'
    simulationAbortedErrorMessage = 'Aborting simulation...\n'

    def __init__(self):
        # Discover in $PATH env var
        found = False
        for path in os.environ.get("PATH").split(os.pathsep):
            executable_route = os.path.join(path, self.__class__.CDPP_BIN)
            if os.path.isfile(executable_route) and os.access(executable_route, os.X_OK):
                found = True
                break
        # Discover in $Wrapper.CDPP_EXECUTABLE_ENV_VAR env var
        if not found:
            try:
                cdpp_bin_directory = os.environ.get(self.__class__.CDPP_EXECUTABLE_ENV_VAR)
                if cdpp_bin_directory != None:
                    executable_route = os.path.join(cdpp_bin_directory, self.__class__.CDPP_BIN)
                    if os.path.isfile(executable_route) and os.access(executable_route, os.X_OK):
                        found = True
            except KeyError as e:
                pass
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