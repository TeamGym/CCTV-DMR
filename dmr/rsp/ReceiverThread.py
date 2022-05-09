import logging
import socket
from threading import Thread

from dmr.util import ConfigHelper

l = logging.getLogger(__name__)
class ReceiverThread(Thread):
    def __init__(self, sock, receiveMessageQueue):
        self.__sock = sock
        self.__receiveMessageQueue = receiveMessageQueue

    def run(self):
        state = ReceiverState.NULL
        while True:
            self.__sock.recv(4096)
