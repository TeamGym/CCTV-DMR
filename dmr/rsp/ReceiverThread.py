import logging
import socket
from threading import Thread
from queue import Queue

from .StreamParser import StreamParser
from .RequestParser import RequestParser
from .ResponseParser import ResponseParser

l = logging.getLogger(__name__)
class ReceiverThread(Thread):
    def __init__(self, sock, onDisconnected):
        super().__init__()
        self.__sock = sock
        self.__receiveMessageQueue = Queue()
        self.__parserList = [
                StreamParser(),
                RequestParser(),
                ResponseParser()]
        self.__onDisconnected = onDisconnected

    @property
    def receiveMessageQueue(self):
        return self.__receiveMessageQueue

    def run(self):
        buffer = bytes(0)
        parser = self.__parserList[0]

        while True:
            received = self.__sock.recv(4096)

            if received == b'':
                self.__onDisconnected()
                return

            buffer += received

            while b'\n' in buffer:
                lineBytes, rest = buffer.split(b'\n', 1)
                buffer = rest

                line = lineBytes.decode('utf-8')

                for i, parser in enumerate(self.__parserList):
                    state, message = parser.parseLine(line)

                    if state == parser.State.DONE:
                        l.debug('received message: \n{}'.format(message.getMessageString()))
                        message.remoteAddress = self.__sock.getpeername()
                        self.__receiveMessageQueue.put(message)
                        parser.reset()

                    if not parser.isFailed():
                        self.__parserList = self.__parserList[i:] + self.__parserList[:i]
                        break

                    parser.reset()
