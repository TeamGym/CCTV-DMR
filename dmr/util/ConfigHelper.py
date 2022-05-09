from typing import Optional

from dmr.classes import Singleton
from dmr.config import GlobalConfig

class ConfigHelper(metaclass=Singleton):
    def __init__(self):
        self.__globalConfig: Optional[GlobalConfig] = None
        self.__path: Optional[str] = None

    @property
    def globalConfig(self):
        if self.__globalConfig is None:
            self.__globalConfig = self.load()
        return self.__globalConfig

    def setGlobalConfigPath(self, path: str):
        self.__path = path

    def load(self) -> GlobalConfig:
        assert self.__path != None
        with open(self.__path, 'r') as file:
            config = GlobalConfig.schema().loads(file.read())
            return config

        raise AssertionError('failed to read config')

