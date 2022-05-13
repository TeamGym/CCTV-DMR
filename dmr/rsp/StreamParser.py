from enum import Enum

from .Stream import Stream
from dmr.rsp.stream_data import DetectionResult
from dmr.rsp.stream_data import ControlPTZ
from dmr.rsp.stream_data import DetectionResultParser
from dmr.rsp.stream_data import ControlPTZParser

class StreamParser:
    def __init__(self):
        self.__state = StreamParser.State.READY
        self.__stream = None
        self.__dataParser = None

    @property
    def state(self):
        return self.__state

    @property
    def stream(self):
        return self.__stream

    @property
    def dataParser(self):
        return self.__dataParser

    def __returnState(self, state, stream=None):
        self.__state = state
        return self.__state, stream

    def isTerminated(self):
        return self.__state.value >= 100

    def isFailed(self):
        return self.__state.value >= 200

    def reset(self):
        self.__state = StreamParser.State.READY
        self.__stream = None
        self.__dataParser = None

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

            channel = None
            streamTypeNumber = None

            try:
                channel = int(tokens[0])
                streamTypeNumber = int(tokens[1])
            except ValueError:
                pass

            if channel is None or streamTypeNumber is None:
                return self.__returnState(StreamParser.State.FAILED)

            streamType = None

            try:
                streamType = Stream.Type(streamTypeNumber)
            except ValueError:
                pass

            if streamType is None:
                return self.__returnState(StreamParser.State.FAILED_INVALID_TYPE)

            self.__stream = Stream(channel, streamType)

            if streamType == Stream.Type.DETECTION_RESULT:
                self.__dataParser = DetectionResultParser()
            elif streamType == Stream.Type.CONTROL_PTZ:
                self.__dataParser = ControlPTZParser()

            self.__state = StreamParser.State.PARSE_DATA

        elif StreamParser.State.PARSE_DATA == self.__state:
            state, data = self.__dataParser.parseLine(line)

            if self.__dataParser.isFailed():
                return self.__returnState(StreamParser.State.FAILED)

            if state == self.__dataParser.State.DONE:
                self.__stream.data = data
                return self.__returnState(StreamParser.State.DONE, self.__stream)

        return self.__state, None

    class State(Enum):
        READY = 0
        PARSE_DATA = 1
        DONE = 100
        FAILED = 200
        FAILED_INVALID_TYPE = 201
