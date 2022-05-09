from enum import Enum

from dmr.rsp import Stream
from dmr.rsp.stream_data import DetectionResult
from dmr.rsp.stream_data import ControlPTZ

class StreamParser:
    def __init__(self):
        self.__state = StreamParser.State.READY
        self.__stream = None

    def __returnState(self, state, request=None):
        self.__state = state
        return self.__state, request

    def isTerminated(self):
        return self.__state.value >= 100

    def isFailed(self):
        return self.__state.value >= 200

    def reset(self):
        self.__state = StreamParser.State.READY
        self.__request = None

    def parseLine(self, line, keepends=False):
        assert not self.isTerminated()

        if keepends:
            line = line[:-1]
            if line[-1] in '\r\n':
                line = line[:-1]

        if StreamParser.State.READY == self.__state:
            if not line.startswith('S'):
                return self.__returnState(StreamParser.State.FAILED)

            line = line[1:]

            if line.count(' ') != 1:
                return self.__returnState(StreamParser.State.FAILED)

            tokens = line.split(' ')

            sessionID = None
            streamTypeNumber = None

            try:
                sessionID = int(tokens[0])
                streamTypeNumber = int(tokens[1])
            except ValueError:
                pass

            if sessionID is None or streamTypeNumber is None:
                return self.__returnState(StreamParser.State.FAILED)

            streamType = None

            try:
                streamType = Stream.Type(streamTypeNumber)
            except ValueError:
                pass

            if streamType is None:
                return self.__returnState(StreamParser.State.FAILED_INVALID_TYPE)

            self.__stream = Stream(sessionID, streamType)

            if Stream.Type.DETECTION_RESULT == streamType:
                self.__state = StreamParser.State.DETECTION_RESULT_READY
            elif Stream.Type.CONTROL_PTZ == streamType:
                self.__state = StreamParser.State.CONTROL_PTZ_READY

        elif StreamParser.State.DETECTION_RESULT_READY == self.__state:
            if line == '':
                return self.__returnState(StreamParser.State.FAILED)

            timestamp = None

            try:
                timestamp = int(line)
            except ValueError:
                pass

            if timestamp is None:
                return self.__returnState(StreamParser.State.FAILED)

            self.__stream.data = DetectionResult(
                    timestamp=timestamp,
                    boxes=[])
            self.__state = StreamParser.State.DETECTION_RESULT_READ_BOX

        elif StreamParser.State.DETECTION_RESULT_READ_BOX == self.__state:
            if line == '':
                return self.__returnState(StreamParser.State.DONE, self.__stream)

            tokens = line.split(',')

            if len(tokens) != 7:
                return self.__returnState(StreamParser.State.FAILED)

            try:
                left = int(tokens[0])
                right = int(tokens[1])
                top = int(tokens[2])
                bottom = int(tokens[3])
                confidence = float(tokens[4])
                classID = int(tokens[5])
                label = tokens[6]

                self.__stream.data.boxes.append(
                        DetectionResult.DetectionBox(
                            left=left,
                            right=right,
                            top=top,
                            bottom=bottom,
                            confidence=confidence,
                            classID=classID,
                            label=label))
            except ValueError:
                return self.__returnState(StreamParser.State.FAILED)

        elif StreamParser.State.CONTROL_PTZ_READY == self.__state:
            if line == '':
                return self.__returnState(StreamParser.State.FAILED)

            tokens = line.split(',')

            if len(tokens) != 3:
                return self.__returnState(StreamParser.State.FAILED)

            try:
                pan = int(tokens[0])
                tilt = int(tokens[1])
                zoom = int(tokens[2])

                self.__stream.data = ControlPTZ(
                        pan=pan,
                        tilt=tilt,
                        zoom=zoom)
                self.__state = StreamParser.State.CONTROL_PTZ_DONE
            except ValueError:
                return self.__returnState(StreamParser.State.FAILED)

        elif StreamParser.State.CONTROL_PTZ_DONE == self.__state:
            if line == '':
                return self.__returnState(StreamParser.State.DONE, self.__stream)

            return self.__returnState(StreamParser.State.FAILED)

        return self.__state, None

    class State(Enum):
        READY = 0
        DETECTION_RESULT_READY = 10
        DETECTION_RESULT_READ_BOX = 11
        CONTROL_PTZ_READY = 20
        CONTROL_PTZ_DONE = 21
        DONE = 100
        FAILED = 200
        FAILED_INVALID_TYPE = 201
