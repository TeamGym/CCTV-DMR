class Response:
    def __init__(self, statusCode, statusMessage, properties={}):
        self.__statusCode = statusCode
        self.__statusMessage = statusMessage
        self.__properties = properties
        self.__sequence = 0

    @property
    def statusCode(self):
        return self.__statusCode

    @statusCode.setter
    def statusCode(self, value):
        self.__statusCode = value

    @property
    def statusMessage(self):
        return self.__statusMessage

    @statusMessage.setter
    def statusMessage(self, value):
        self.__statusMessage = value

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
