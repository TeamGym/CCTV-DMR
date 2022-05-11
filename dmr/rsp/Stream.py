from enum import Enum

class Stream:
    def __init__(self, channel, streamType, data=None):
        self.__channel = channel
        self.__streamType = streamType
        self.__data = data

    @property
    def channel(self):
        return self.__channel

    @channel.setter
    def channel(self, value):
        self.__channel = value

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

    def getMessageString(self):
        streamLine = 'S' + str(self.__channel) + ' ' + str(self.__streamType.value) + '\n'

        return streamLine \
                + self.__data.getMessageString() \
                + '\n'

    class Type(Enum):
        DETECTION_RESULT = 1
        CONTROL_PTZ = 2
