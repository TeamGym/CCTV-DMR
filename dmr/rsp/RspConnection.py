import logging
import socket
from threading import Thread, RLock
from queue import Queue

from .EndpointType import EndpointType
from .SenderThread import SenderThread
from .ReceiverThread import ReceiverThread
from .MessageEventThread import MessageEventThread

l = logging.getLogger(__name__)
class RspConnection:
    def __init__(self,
            endpointType,
            sock,
            streamHandlers=None,
            requestHandlers=None,
            eventHandlers=None):
        self.__endpointType = endpointType
        self.__sock = sock

        self.__streamHandlers = streamHandlers or {}
        self.__requestHandlers = requestHandlers or {}

        self.__eventHandlers = {
                'Disconnected': [],
                **(eventHandlers or {})
                }

        self.__senderThread = None
        self.__receiverThread = None
        self.__messageEventThread = None

        self.__eventLock = RLock()

        self.__sequenceCount = 0

    # ----------------------------------------------------------------------
    # Property
    # ----------------------------------------------------------------------

    @property
    def endpointType(self):
        return self.__endpointType

    @property
    def sock(self):
        return self.__sock

    # ----------------------------------------------------------------------
    # Private Method
    # ----------------------------------------------------------------------

    def __fireEvent(self, event, *args):
        with self.__eventLock:
            for handler in self.__eventHandlers[event]:
                handler(*args)

    def __onRequestReceived(self, request):
        with self.__eventLock:
            if request.method in self.__requestHandlers:
                self.__requestHandlers[request.method](request,
                        lambda response: self.sendResponse(response, request))

    def __onStreamReceived(self, stream):
        with self.__eventLock:
            if stream.channel in self.__streamHandlers:
                self.__streamHandlers[stream.channel](stream)
            if 0 in self.__streamHandlers:
                self.__streamHandlers[0](stream)

    def __onDisconnected(self):
        self.__fireEvent('Disconnected', self.__sock.getpeername())

    # ----------------------------------------------------------------------
    # Public Method
    # ----------------------------------------------------------------------

    def sendRequest(self, request):
        request.connection = self
        request.sequence = self.__sequenceCount
        self.__sequenceCount = (self.__sequenceCount + 1) % 2**32

        self.__senderThread.messageQueue.put(request)

    def sendResponse(self, response, requestReceived):
        assert not requestReceived.delivered

        requestReceived.delivered = True
        response.sequence = requestReceived.sequence

        response.connection = self

        self.__senderThread.messageQueue.put(response)

    def sendStream(self, stream):
        stream.connection = self

        self.__senderThread.messageQueue.put(stream)

    def addRequestHandler(self, method, handler):
        with self.__eventLock:
            self.__requestHandlers[method] = handler

    def addStreamHandler(self, channel, handler):
        with self.__eventLock:
            self.__streamHandlers[channel] = handler

    def addEventHandler(self, event, handler):
        with self.__eventLock:
            self.__eventHandlers[event].append(handler)

    def removeRequestHandler(self, method):
        with self.__eventLock:
            del self.__requestHandlers[method]

    def removeStreamHandler(self, channel):
        with self.__eventLock:
            del self.__streamHandlers[channel]

    def removeEventHandler(self, event, handler):
        with self.__eventLock:
            self.__eventHandlers[event].remove(handler)

    def start(self):
        assert self.__senderThread is None and \
                self.__receiverThread is None and \
                self.__messageEventThread is None

        self.__senderThread = SenderThread(
                sock=self.__sock)
        self.__senderThread.daemon = True

        self.__receiverThread = ReceiverThread(
                sock=self.__sock,
                onDisconnected=self.__onDisconnected)
        self.__receiverThread.daemon = True

        self.__messageEventThread = MessageEventThread(
                connection=self,
                receivedMessageQueue=self.__receiverThread.receivedMessageQueue,
                sentRequestDict=self.__senderThread.sentRequestDict,
                onRequestReceived=self.__onRequestReceived,
                onStreamReceived=self.__onStreamReceived)
        self.__messageEventThread.daemon = True

        self.__senderThread.start()
        self.__receiverThread.start()
        self.__messageEventThread.start()

    def close(self):
        l.debug('Close Connection remote={}'.format(self.__sock.getpeername()))
        self.__sock.shutdown(socket.SHUT_RDWR)
        self.__sock.close()
        self.__senderThread.messageQueue.put(None)
        self.__receiverThread.receivedMessageQueue.put(None)

    # ----------------------------------------------------------------------
    # Class Method
    # ----------------------------------------------------------------------

    @classmethod
    def makeConnection(cls,
            endpointType,
            remote,
            streamHandlers=None,
            requestHandlers=None,
            eventHandlers=None):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(remote)

        conn = RspConnection(
                endpointType,
                sock,
                streamHandlers,
                requestHandlers,
                eventHandlers)
        conn.start()

        return conn
