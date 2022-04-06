import logging
from twisted.internet import reactor
from twisted.web.server import Site

from dmr.classes import Singleton
from dmr.utils import ConfigHelper

l = logging.getLogger(__name__)
settings = ConfigHelper().globalConfig.globalSettings
class WebServer(metaclass=Singleton):
    app = Klein()

    @app.route('/')
    def root(self, request):
        l.info('access to {}, from {}'.format(request.uri, request.getHost()))
        return settings.to_json()

    def run(self):
        l.info('Web server start on {}'.format(settings.webPort))
        reactor.listenTCP(settings.webPort, Site(self.app.resource())

    def stop(self):
        l.info('Web server stop')
        reactor.stop()

