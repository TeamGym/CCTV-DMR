import logging
import socket
from threading import Thread

from multiprocessing import Queue

from dmr.classes import Singleton
from dmr.util import ConfigHelper

from .SenderThread import SenderThread
from .ReceiverThread import ReceiverThread

l = logging.getLogger(__name__)
config = ConfigHelper().globalConfig
settings = config.globalSettings
class TcpRelayServer(metaclass=Singleton):
    def __init__(self):
        self.__thread = None
        self.__server = None

        self.__clients = []

        self.__sendMessageQueue = Queue()
        self.__receiveMessageQueue = Queue()

    def start(self):
        assert self.__thread is None
        self.__thread = Thread(target=self.run)
        self.__thread.daemon = True
        self.__thread.start()

    def run(self):
        l.info('TCP Server start on {}'.format(settings.tcpPort))
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.bind(('', settings.tcpPort))
        self.__server.listen(10)
        self.__server.setblocking(True)

        while True:
            (clientsocket, address) = self.__server.accept()
            l.info('TCP Connection from {address}')
            self.__clients.append(RspConnection(EndpointType.DMR, clientsocket))

    def stop(self):
        l.info('TCP Server stop')
        self.__running = False
        self.__server.shutdown(socket.SHUT_RDWR) # not tested
        self.__server.close()

