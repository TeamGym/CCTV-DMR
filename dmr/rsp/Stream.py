from enum import Enum

class Stream:
    def __init__(self, sessionID, streamType):
        self.__sessionID = sessionID
        self.__streamType = streamType
        self.__data = None

    @property
    def sessionID(self):
        return self.__sessionID

    @sessionID.setter
    def sessionID(self, value):
        self.__sessionID = value

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value):
        self.__data = value

    @property
    def streamType(self):
        return self.__streamType

    @streamType.setter
    def streamType(self, value):
        self.__streamType = value

    class Type(Enum):
        DETECTION_RESULT = 1
        CONTROL_PTZ = 2
