from enum import Enum

from .Response import Response
from .Rsp import Rsp

class ResponseParser:
    def __init__(self):
        self.__state = ResponseParser.State.READY
        self.__response = None

    @property
    def state(self):
        return self.__state

    @property
    def response(self):
        return self.__response

    def __returnState(self, state, response=None):
        self.__state = state
        return self.__state, response

    def isTerminated(self):
        return self.__state.value >= 100

    def isFailed(self):
        return self.__state.value >= 200

    def reset(self):
        self.__state = ResponseParser.State.READY
        self.__response = None

    def parseLine(self, line, keepends=False):
        assert not self.isTerminated()

        if keepends:
            line = line[:-1]
            if line[-1] in '\r\n':
                line = line[:-1]

        if ResponseParser.State.READY == self.__state:
            if line.count(' ') != 1:
                return self.__returnState(ResponseParser.State.FAILED)

            protocol, statusCodeStr = line.split(' ')

            if protocol.count('/') != 1:
                return self.__returnState(ResponseParser.State.FAILED_INVALID_PROTOCOL)

            protocolName, protocolVersion = protocol.split('/')

            if protocolName != 'RSP' or protocolVersion != Rsp.VERSION:
                return self.__returnState(ResponseParser.State.FAILED_INVALID_PROTOCOL)

            statusCode = None
            try:
                statusCode = int(statusCodeStr)
            except ValueError:
                pass

            if statusCode is None:
                return self.__returnState(ResponseParser.State.FAILED_INVALID_STATUS)

            self.__response = Response(statusCode)
            self.__state = ResponseParser.State.PARSE_SEQUENCE

        elif ResponseParser.State.PARSE_SEQUENCE == self.__state:
            if not line.startswith('Seq='):
                return self.__returnState(ResponseParser.State.FAILED)

            sequenceNumber = None
            try:
                sequenceNumber = int(line[4:])
            except ValueError:
                pass

            if sequenceNumber is None:
                return self.__returnState(ResponseParser.State.FAILED)

            self.__response.sequence = sequenceNumber
            self.__state = ResponseParser.State.PARSE_PROPERTY

        elif ResponseParser.State.PARSE_PROPERTY == self.__state:
            if line == '':
                return self.__returnState(ResponseParser.State.DONE, self.__response)

            if '=' not in line:
                return self.__returnState(ResponseParser.State.FAILED)

            propertyName, propertyValue = line.split('=', maxsplit=1)

            self.__response.addProperty(propertyName, propertyValue)

        return self.__state, None

    class State(Enum):
        READY = 0
        PARSE_SEQUENCE = 1
        PARSE_PROPERTY = 2
        DONE = 100
        FAILED = 200
        FAILED_INVALID_PROTOCOL = 201
        FAILED_INVALID_STATUS = 202
