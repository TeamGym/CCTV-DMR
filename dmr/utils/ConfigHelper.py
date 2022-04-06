from dmr.classes import Singleton
from dmr.config import GlobalConfig

class ConfigHelper(metaclass=Singleton):
    def __init__(self):
        self.__globalConfig = None

    @property
    def globalConfig(self):
        if self.__globalConfig is None:
            self.__globalConfig = self.load()
        return self.__globalConfig

    def setGlobalConfigPath(self, path: str):
        self.__path = path

    def load(self) -> GlobalConfig:
        with open(self.__path, 'r') as file:
            config = GlobalConfig.schema().loads(file.read())
            return config

        raise AssertionError('failed to read config')

