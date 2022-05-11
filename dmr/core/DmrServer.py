import signal
import logging

from dmr.classes import Singleton
#from dmr.web_server import WebServer
#from dmr.rtsp_server import RtspRelayServer
from dmr.streaming_server import StreamingServer
from dmr.tcp_server import TcpRelayServer
#from dmr.tcp_server_2 import TcpRelayServer

l = logging.getLogger(__name__)
class DmrServer(metaclass=Singleton):
    def __init__(self):
        #self.__webServer = WebServer()
        #self.__rtspRelayServer = RtspRelayServer()
        self.__tcpRelayServer = TcpRelayServer()
        self.__streamingServer = StreamingServer()

    def onSigInt(self, sig, frame) -> None:
        #self.__webServer.stop()
        #self.__rtspRelayServer.stop()
        self.__tcpRelayServer.stop()
        self.__streamingServer.stop()

    def run(self) -> None:
        signal.signal(signal.SIGINT, self.onSigInt)
        l.info('Start DmrServer')
        self.__streamingServer.start()
        #self.__rtspRelayServer.start()
        self.__tcpRelayServer.run()
        #self.__webServer.run()

