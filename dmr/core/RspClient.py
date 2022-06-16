from dataclasses import dataclass
from typing import List

from threading import RLock

from dmr.rsp import RspConnection, Request
from dmr.tunnel import UdpRelayTunnel
from dmr.tunnel import StreamRelayTunnel

l = logging.getLogger(__name__)
class RspClient:
    def __init__(self, connection, tunnelContainer):
        self.__connection = connection
        self.__tunnelContainer = tunnelContainer

        self.__connection.addRequestHandler(Request.Method.JOIN, self.__onJoin)
        self.__connection.addRequestHandler(Request.Method.LEAVE, self.__onLeave)
        self.__connection.addStreamHandler(0, self.__onStream)
        self.__connection.addEventHandler('Disconnected', self.__onDisconnected)

    def __onJoin(self, request, returnResponse):
        tunnelType = request.getProperty('Type')
        tunnel = None
        listen = None
        try:
            tunnel = int(request.getProperty('Tunnel'))
            listen = int(request.getProperty('Listen'))
        except:
            returnResponse(Response(statusCode=400))
            return

        ret = False
        if tunnelType == 'UDP':
            ret = self.__tunnelContainer.joinUdp(self.__connection, tunnel, listen)
        elif tunnelType == 'STREAM':
            ret, channel = self.__tunnelContainer.joinStream(self.__connection, tunnel, listen)
            listen = channel

        if ret:
            returnResponse(Response(
                statusCode=200,
                properties={'Listen': listen}))
        else:
            returnResponse(Response(statusCode=400))

        return

    def __onLeave(self, request, returnResponse):
        tunnelType = request.getProperty('Type')
        tunnel = None
        listen = None
        try:
            tunnel = int(request.getProperty('Tunnel'))
            listen = int(request.getProperty('Listen'))
        except:
            returnResponse(Response(statusCode=400))
            return

        ret = False
        if tunnelType == 'UDP':
            ret = self.__tunnelContainer.leaveUdp(self.__connection, tunnel, listen)
        elif tunnelType == 'STREAM':
            ret = self.__tunnelContainer.leaveStream(self.__connection, tunnel, listen)

        if ret:
            returnResponse(Response(statusCode=200))
        else:
            returnResponse(Response(statusCode=400))

        return

    def __onDisconnected(self, address):
        self.__tunnelContainer.removeConnection(self.__connection)

        l.info('Disconnected (address={})'.format(self.__getAddress()))

    def __onStream(self, stream):
        self.__tunnelContainer.broadcastStream(stream)
