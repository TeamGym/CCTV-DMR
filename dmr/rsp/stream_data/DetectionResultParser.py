from enum import Enum

from .DetectionResult import DetectionResult

class DetectionResultParser:
    def __init__(self):
        self.__state = DetectionResultParser.State.READY
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
        if DetectionResultParser.State.READY == self.__state:
            if line == '':
                return self.__returnState(DetectionResultParser.State.FAILED)

            timestamp = None

            try:
                timestamp = int(line)
            except ValueError:
                pass

            if timestamp is None:
                return self.__returnState(DetectionResultParser.State.FAILED)

            self.__data = DetectionResult(
                    timestamp=timestamp,
                    boxes=[])
            self.__state = DetectionResultParser.State.READ_BOX

        elif DetectionResultParser.State.READ_BOX == self.__state:
            if line == '':
                return self.__returnState(DetectionResultParser.State.DONE, self.__data)

            tokens = line.split(',')

            if len(tokens) != 7:
                return self.__returnState(DetectionResultParser.State.FAILED)

            try:
                left = int(tokens[0])
                right = int(tokens[1])
                top = int(tokens[2])
                bottom = int(tokens[3])
                confidence = float(tokens[4])
                classID = int(tokens[5])
                label = tokens[6]

                self.__data.boxes.append(
                        DetectionResult.DetectionBox(
                            left=left,
                            right=right,
                            top=top,
                            bottom=bottom,
                            confidence=confidence,
                            classID=classID,
                            label=label))
            except ValueError:
                return self.__returnState(DetectionResultParser.State.FAILED)

        return self.__state, None

    class State(Enum):
        READY = 0
        READ_BOX = 1
        DONE = 100
        FAILED = 200
