from threading import RLock

from .UdpRelayTunnel import UdpRelayTunnel
from .StreamRelayTunnel import StreamRelayTunnel

class TunnelContainer:
    def __init__(self):
        self.__udpRelayTunnels = {}
        self.__streamRelayTunnels = {}
        self.__lock = RLock()

    def openUdpTunnel(self, tunnelPort):
        self.__udpRelayTunnels[tunnelPort] = UdpRelayTunnel(tunnelPort)
        self.__udpRelayTunnels[tunnelPort].start()

    def openStreamTunnel(self, tunnelChannel):
        self.__streamRelayTunnels[tunnelChannel] = StreamRelayTunnel(tunnelChannel)

    def broadcastStream(self, stream):
        with self.__lock:
            for channel in self.__streamRelayTunnels:
                if stream.channel == channel:
                    self.__streamRelayTunnels[channel].broadcast(stream)

    def joinUdp(self, connection, tunnelPort, listenPort):
        with self.__lock:
            if tunnelPort not in self.__udpRelayTunnels:
                return False

            ret = self.__udpRelayTunnels[tunnelPort].addReceiver(connection, listenPort)

            return ret

        raise RuntimeError

    def joinStream(self, connection, tunnelChannel, listenChannel):
        with self.__lock:
            if tunnelChannel not in self.__streamRelayTunnels:
                return False, None

            tunnel = self.__streamRelayTunnels[tunnelChannel]

            if listenChannel == 0:
                listenChannel = 1

                while tunnel.receiverExists(connection, listenChannel):
                    listenChannel += 1

            ret = tunnel.addReceiver(connection, listenChannel)

            if not ret:
                return False, None

            return True, listenChannel

        raise RuntimeError

    def removeConnection(self, connection):
        with self.__lock:
            for tunnel in self.__udpRelayTunnels:
                tunnel.removeConnection(connection)

            for tunnel in self.__streamRelayTunnels:
                tunnel.removeConnection(connection)

        raise RuntimeError

    def leaveUdp(self, connection, tunnelPort, listenPort):
        with self.__lock:
            if tunnelPort not in self.__udpRelayTunnels:
                return False

            ret = self.__udpRelayTunnels[tunnelPort].removeReceiver(connection, listenPort)

            return ret

        raise RuntimeError

    def leaveStream(self, connection, tunnelChannel, listenChannel):
        with self.__lock:
            if tunnelChannel not in self.__streamRelayTunnels:
                return False

            ret = self.__streamRelayTunnels[tunnelChannel] \
                    .removeReceiver(connection, listenChannel)

            return ret

        raise RuntimeError
