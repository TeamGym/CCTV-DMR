import logging
from threading import Thread

from .Request import Request
from .Response import Response
from .Stream import Stream

l = logging.getLogger(__name__)
class MessageEventThread(Thread):
    def __init__(self,
            connection,
            receivedMessageQueue,
            sentRequestDict,
            onRequestReceived,
            onStreamReceived):
        super().__init__()
        self.__connection = connection
        self.__receivedMessageQueue = receivedMessageQueue
        self.__sentRequestDict = sentRequestDict
        self.__onRequestReceived = onRequestReceived
        self.__onStreamReceived = onStreamReceived

    def run(self):
        while True:
            message = self.__receivedMessageQueue.get()
            if message is None:
                break

            message.connection = self.__connection

            if isinstance(message, Stream):
                self.__onStreamReceived(message)
            elif isinstance(message, Request):
                self.__onRequestReceived(message)
            elif isinstance(message, Response):
                if message.sequence not in self.__sentRequestDict:
                    l.debug('no matching request for response, sequence number = {}'
                            .format(message.sequence))
                    return

                self.__sentRequestDict[message.sequence].onResponseCallback(message)
                del self.__sentRequestDict[message.sequence]
