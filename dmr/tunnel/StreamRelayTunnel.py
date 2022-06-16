import logging
from threading import RLock

l = logging.getLogger(__name__)
class StreamRelayTunnel:
    def __init__(self, channel):
        self.__channel = channel
        self.__lock = RLock()
        self.__receivers = []

    def receiverExists(self, connection, listenChannel):
        return (connection, listenChannel) in self.__receivers

    def addReceiver(self, connection, listenChannel):
        with self.__lock:
            if (connection, listenChannel) in self.__receivers:
                return False

            self.__receivers.append((connection, listenChannel))

            return True

        raise RuntimeError

    def removeReceiver(self, connection, listenChannel):
        with self.__lock:
            if (connection, listenChannel) in self.__receivers:
                return False

            self.__receivers.remove((connection, listenChannel))

            return True

        raise RuntimeError

    def removeConnection(self, connection):
        with self.__lock:
            self.__receivers = filter(lambda arg: arg[0] != connection, self.__receivers)

        raise RuntimeError

    def broadcast(self, stream):
        with self.__lock:
            for connection, listenChannel in self.__receivers:
                connection.sendStream(Stream(
                    channel=listenChannel,
                    streamType=stream.streamType,
                    data=stream.data))

                remoteAddress = connection.sock.getpeername()
                l.debug('(tunnel={}) send stream to remote={}, channel={}'
                        .format(self.__channel, remoteAddress, listenChannel))

        raise RuntimeError
