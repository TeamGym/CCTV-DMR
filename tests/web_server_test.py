from dmr.utils import ConfigHelper
from dmr.web_server import WebServer

ConfigHelper().setGlobalConfigPath('config.json')
webServer = WebServer()
webServer.run()

