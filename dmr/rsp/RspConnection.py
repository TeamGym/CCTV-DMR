import logging
import socket
from threading import Thread
from multiprocessing import Queue

from .EndpointType import EndpointType

l = logging.getLogger(__name__)
class RspConnection:
    def __init__(self, endpointType, sock):
        self.__endpointType = endpointType
        self.__sock = sock

        self.__eventHandlers = {
                'Connected': []
                }

        self.__senderThread = None
        self.__receiverThread = None

        self.__sendMessageQueue = Queue()
        self.__receiveMessageQueue = Queue()

        self.start()
        l.debug('Connecting')

    @classmethod
    def makeConnection(cls, endpointType, remote):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.start(remote)

        return RspConnection(endpointType, sock)

    @property
    def sendMessageQueue(self):
        return self.__sendMessageQueue

    @property
    def receiveMessageQueue(self):
        return self.__receiveMessageQueue

    def start(self):
        assert self.__senderThread is not None and \
                self.__receiverThread is not None

        self.__senderThread = SenderThread(self.__sendMessageQueue)
        self.__senderThread.daemon = True

        self.__receiverThread = ReceiverThread(self.__receiveMessageQueue)
        self.__receiverThread.daemon = True

        self.__senderThread.start()
        self.__receiverThread.start()

        # TODO: RSP Handshake
