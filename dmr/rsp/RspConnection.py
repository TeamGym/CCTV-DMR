import logging
import socket
from threading import Thread
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
            streamHandlers={},
            requestHandlers={},
            eventHandlers={}):
        self.__endpointType = endpointType
        self.__sock = sock

        self.__streamHandlers = streamHandlers
        self.__requestHandlers = requestHandlers

        self.__eventHandlers = {
                'Disconnected': [],
                **eventHandlers
                }

        self.__senderThread = None
        self.__receiverThread = None
        self.__messageEventThread = None

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
        for handler in self.__eventHandlers[event]:
            handler(*args)

    def __onRequestReceived(self, request):
        if request.method in self.__requestHandlers:
            self.__requestHandlers[request.method](request,
                    lambda response: self.sendResponse(response, request))

    def __onStreamReceived(self, stream):
        if stream.channel in self.__streamHandlers:
            self.__streamHandlers[stream.channel](stream)

    def __onDisconnected(self):
        self.__fireEvent('Disconnected', self.__sock.getpeername())

    # ----------------------------------------------------------------------
    # Public Method
    # ----------------------------------------------------------------------

    def sendRequest(self, request):
        request.sequence = self.__sequenceCount
        self.__sequenceCount = (self.__sequenceCount + 1) % 2**32

        self.__senderThread.sendMessageQueue.put(request)

    def sendResponse(self, response, requestReceived):
        assert not requestReceived.delivered

        requestReceived.delivered = True
        response.sequence = requestReceived.sequence

        self.__senderThread.sendMessageQueue.put(response)

    def sendStream(self, stream):
        self.__senderThread.sendMessageQueue.put(stream)

    def addRequestHandler(self, method, handler):
        self.__requestHandlers[method] = handler

    def addStreamHandler(self, channel, handler):
        self.__streamHandlers[channel] = handler

    def addEventHandler(self, event, handler):
        self.__eventHandlers[event].append(handler)

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
                receiveMessageQueue=self.__receiverThread.receiveMessageQueue,
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
        self.__senderThread.sendMessageQueue.put(None)
        self.__receiverThread.receiveMessageQueue.put(None)

    # ----------------------------------------------------------------------
    # Class Method
    # ----------------------------------------------------------------------

    @classmethod
    def makeConnection(cls,
            endpointType,
            remote,
            streamHandlers={},
            requestHandlers={},
            eventHandlers={}):
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
