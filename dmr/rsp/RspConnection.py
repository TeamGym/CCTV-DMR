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
            requestHandlers={}):
        self.__endpointType = endpointType
        self.__sock = sock

        self.__streamHandlers = streamHandlers
        self.__requestHandlers = requestHandlers

        self.__senderThread = None
        self.__receiverThread = None
        self.__messageEventThread = None

        self.__sequenceCount = 0

        self.start()

    @classmethod
    def makeConnection(cls,
            endpointType,
            remote,
            streamHandlers={},
            requestHandlers={}):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(remote)

        return RspConnection(endpointType, sock, streamHandlers, requestHandlers)

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

    def __fireEvent(self, event, *args):
        for handler in self.__eventHandlers[event]:
            handler(*args)

    def __onRequestReceived(self, request):
        if request.method in self.__requestHandlers:
            self.__requestHandlers[request.method](request,
                    lambda response: self.sendResponse(response, request))

    def __onStreamReceived(self, stream):
        if stream.streamType in self.__streamHandlers:
            self.__streamHandlers[stream.streamType](stream)

    def addRequestHandler(self, method, handler):
        self.__requestHandlers[method] = handler

    def addStreamHandler(self, streamType, handler):
        self.__streamHandlers[streamType] = handler

    def start(self):
        assert self.__senderThread is None and \
                self.__receiverThread is None and \
                self.__messageEventThread is None

        self.__senderThread = SenderThread(
                sock=self.__sock)
        self.__senderThread.daemon = True

        self.__receiverThread = ReceiverThread(
                sock=self.__sock)
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

        l.debug('Start Connection')

        # TODO: RSP Handshake
