from enum import Enum

from .Request import Request
from .Rsp import Rsp

class RequestParser:
    def __init__(self):
        self.__state = RequestParser.State.READY
        self.__request = None

    def __returnState(self, state, request=None):
        self.__state = state
        return self.__state, request

    def isTerminated(self):
        return self.__state.value >= 100

    def isFailed(self):
        return self.__state.value >= 200

    def reset(self):
        self.__state = RequestParser.State.READY
        self.__request = None

    def parseLine(self, line, keepends=False):
        assert not self.isTerminated()

        if keepends:
            line = line[:-1]
            if line[-1] in '\r\n':
                line = line[:-1]

        if RequestParser.State.READY == self.__state:
            tokens = line.split(' ')
            if len(tokens) != 2:
                return self.__returnState(RequestParser.State.FAILED)

            method = tokens[0]
            protocol = tokens[1]

            if protocol.count('/') != 1:
                return self.__returnState(RequestParser.State.FAILED_INVALID_PROTOCOL)

            protocolName, protocolVersion = protocol.split('/')

            if protocolName != 'RSP' or protocolVersion != Rsp.VERSION:
                return self.__returnState(RequestParser.State.FAILED_INVALID_PROTOCOL)

            methodType = None

            try:
                methodType = Request.Method[method]
            except KeyError:
                pass

            if methodType is None:
                return self.__returnState(RequestParser.State.FAILED_INVALID_METHOD)

            self.__request = Request(methodType)
            self.__state = RequestParser.State.PARSE_SEQUENCE

        elif RequestParser.State.PARSE_SEQUENCE == self.__state:
            if not line.startswith('Seq='):
                return self.__returnState(RequestParser.State.FAILED)

            sequenceNumber = None

            try:
                sequenceNumber = int(line[4:])
            except ValueError:
                pass

            if sequenceNumber is None:
                return self.__returnState(RequestParser.State.FAILED)

            self.__request.sequence = sequenceNumber
            self.__state = RequestParser.State.PARSE_PROPERTY

        elif RequestParser.State.PARSE_PROPERTY == self.__state:
            if line == '':
                return self.__returnState(RequestParser.State.DONE, self.__request)

            if '=' not in line:
                return self.__returnState(RequestParser.State.FAILED)

            propertyName, propertyValue = line.split('=', maxsplit=1)

            self.__request.addProperty(propertyName, propertyValue)

        return self.__state, None

    class State(Enum):
        READY = 0
        PARSE_SEQUENCE = 1
        PARSE_PROPERTY = 2
        DONE = 100
        FAILED = 200
        FAILED_INVALID_PROTOCOL = 201
        FAILED_INVALID_METHOD = 202
