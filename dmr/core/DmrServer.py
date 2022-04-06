import signal
import logging

from dmr.classes import Singleton
from dmr.web_server import WebServer
from dmr.rtsp_server import RtspRelayServer
from dmr.tcp_server import TcpRelayServer

l = logging.getLogger(__name__)
class DmrServer(metaclass=Singleton):

    def __init__(self):
        self.__webServer = WebServer()
        self.__rtspRelayServer = RtspRelayServer()
        self.__tcpRelayServer = TcpRelayServer()

    def onSigInt(self, sig, frame) -> None:
        pass

    def run(self) -> None:
        signal.signal(signal.SIGINT, self.onSigInt)
        l.info('Start DmrServer')
        self.__webServer.start()
        self.__rtspRelayServer.start()
        self.__tcpRelayServer.start()

