import logging
import json
from klein import Klein
from twisted.internet import reactor
from twisted.web.server import Site

from dmr.classes import Singleton
from dmr.util import ConfigHelper

l = logging.getLogger(__name__)
config = ConfigHelper().globalConfig
settings = config.globalSettings
class WebServer(metaclass=Singleton):
    app = Klein()

    @app.route('/')
    def root(self, request) -> str:
        l.info('access {}, client: {}'.format(request.uri, request.getHost()))

        response = {
                'httpPort': settings.httpPort,
                'tcpPort': settings.tcpPort,
                'cameraList': []}

        for camConfig in config.cameraConfigs:
            response['cameraList'].append({
                'id': camConfig.camId,
                'name': camConfig.name})

        return json.dumps(response)

    def run(self) -> None:
        l.info('Web Server start on {}'.format(settings.httpPort))
        reactor.listenTCP(settings.httpPort, Site(self.app.resource()))
        reactor.run()

    def stop(self) -> None:
        l.info('Web Server stop')
        reactor.stop()

