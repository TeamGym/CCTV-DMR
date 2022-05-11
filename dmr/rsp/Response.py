from .Rsp import Rsp

class Response:
    def __init__(self, statusCode, properties={}):
        self.__statusCode = statusCode
        self.__properties = properties
        self.__sequence = 0

    @property
    def statusCode(self):
        return self.__statusCode

    @statusCode.setter
    def statusCode(self, value):
        self.__statusCode = value

    @property
    def sequence(self):
        return self.__sequence

    @sequence.setter
    def sequence(self, value):
        self.__sequence = value

    def getProperties(self):
        return self.__properties.keys()

    def getProperty(self, key):
        return self.__properties.get(key)

    def addProperty(self, key, value):
        self.__properties[key] = value

    def getMessageString(self):
        responseLine = 'RSP/' + Rsp.VERSION + ' ' + str(self.__statusCode) + '\n'
        sequenceLine = 'Seq=' + str(self.__sequence) + '\n'
        propertyLines = []

        for name, value in self.__properties.items():
            propertyLines.append(name + '=' + value + '\n')

        return responseLine \
                + sequenceLine \
                + ''.join(propertyLines) \
                + '\n'
