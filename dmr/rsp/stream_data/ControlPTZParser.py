from enum import Enum

from .ControlPTZ import ControlPTZ

class ControlPTZParser:
    def __init__(self):
        self.__state = ControlPTZParser.State.READY
        self.__data = None

    @property
    def state(self):
        return self.__state

    @property
    def data(self):
        return self.__data

    def __returnState(self, state, data=None):
        self.__state = state
        return self.__state, data

    def isFailed(self):
        return self.__state.value >= 200

    def parseLine(self, line):
        if ControlPTZParser.State.READY == self.__state:
            if line == '':
                return self.__returnState(ControlPTZParser.State.FAILED)

            tokens = line.split(',')

            if len(tokens) != 3:
                return self.__returnState(ControlPTZParser.State.FAILED)

            try:
                pan = int(tokens[0])
                tilt = int(tokens[1])
                zoom = int(tokens[2])

                self.__data = ControlPTZ(
                        pan=pan,
                        tilt=tilt,
                        zoom=zoom)
                self.__state = ControlPTZParser.State.READ_NEWLINE
            except ValueError:
                return self.__returnState(ControlPTZParser.State.FAILED)

        elif ControlPTZParser.State.READ_NEWLINE == self.__state:
            if line == '':
                return self.__returnState(ControlPTZParser.State.DONE, self.__data)

            return self.__returnState(ControlPTZParser.State.FAILED)

        return self.__state, None

    class State(Enum):
        READY = 0
        READ_NEWLINE = 1
        DONE = 100
        FAILED = 200
