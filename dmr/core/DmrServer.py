import sys
import signal
import logging
import socket
from threading import RLock

from dmr.rsp import EndpointType, RspConnection, Request, Response
from dmr.tunnel import TunnelContainer
from dmr.util import Singleton
from dmr.util import ConfigHelper

l = logging.getLogger(__name__)
config = ConfigHelper().globalConfig
settings = config.globalSettings
class DmrServer(metaclass=Singleton):
    def __init__(self):
        self.__tunnelContainer = TunnelContainer()
        self.__clients = {}
        self.__listenPorts = {}

        self.__lock = RLock()
        self.__running = False
        self.__serverSocket = None

    def onSigInt(self, sig, frame) -> None:
        l.info('Stop DmrServer')

        self.__running = False
        with self.__lock:
            for client in self.__clients:
                self.__clients[client].close()
        self.__serverSocket.close()

        with self.__lock:
            for tunnel in self.__udpRelayTunnels.values():
                tunnel.stop()
                tunnel.join(1)

        sys.exit(0)

    def run(self) -> None:
        """Start DMR Server on current thread."""

        signal.signal(signal.SIGINT, self.onSigInt)
        l.info('Start DmrServer on {}'.format(settings.serverPort))

        self.__running = True

        for cam in config.cameraConfigs:
            self.__tunnelContainer.openUdpTunnel(cam.videoPort)
            self.__tunnelContainer.openUdpTunnel(cam.audioInPort)
            self.__tunnelContainer.openUdpTunnel(cam.audioOutPort)
            self.__tunnelContainer.openStreamTunnel(cam.inChannel)
            self.__tunnelContainer.openStreamTunnel(cam.outChannel)

        self.__serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__serverSocket.bind(('', settings.serverPort))
        self.__serverSocket.listen(10)
        self.__serverSocket.setblocking(True)

        while self.__running:
            try:
                (clientSocket, address) = self.__serverSocket.accept()
                l.info('Connected from {}'.format(clientSocket.getpeername()))

                conn = RspConnection(
                    endpointType=EndpointType.DMR,
                    sock=clientSocket,
                    requestHandlers={
                        Request.Method.GET_INFO: self.onGetInfo})

                self.__clients[clientSocket.getpeername()] = RspClient(conn, tunnelContainer)
                conn.start()
            except OSError as e:
                if e.errno != 9:
                    raise e

    # ----------------------------------------------------------------------
    # RSP Request Handler
    # ----------------------------------------------------------------------

    def onGetInfo(self, request, returnResponse):
        response = Response(statusCode=200)

        response.addProperty('CamList',
                ','.join([str(camera.camId) for camera in config.cameraConfigs]))

        for camera in config.cameraConfigs:
            response.addProperty('Cam{}-Name'.format(camera.camId), camera.name)
            response.addProperty('Cam{}-VideoPort'.format(camera.camId), str(camera.videoPort))
            response.addProperty('Cam{}-AudioInPort'.format(camera.camId), str(camera.audioInPort))
            response.addProperty('Cam{}-AudioOutPort'.format(camera.camId), str(camera.audioOutPort))
            response.addProperty('Cam{}-InChannel'.format(camera.camId), str(camera.inChannel))
            response.addProperty('Cam{}-OutChannel'.format(camera.camId), str(camera.outChannel))

        returnResponse(response)

#    def onJoin(self, request, returnResponse):
#        tunnelType = request.getProperty('Type')
#        tunnel = None
#        listen = None
#        try:
#            tunnel = int(request.getProperty('Tunnel'))
#            listen = int(request.getProperty('Listen'))
#        except:
#            returnResponse(Response(statusCode=400))
#            return
#
#        remoteIp, remotePort = request.remoteAddress
#
#        if tunnelType == 'UDP':
#            with self.__lock:
#                if tunnel not in self.__udpRelayTunnels:
#                    returnResponse(Response(statusCode=400))
#                    return
#
#                ret = self.__clients[request.remoteAddress] \
#                        .joinUdp(self.__udpRelayTunnels[tunnel], remoteIp, listen)
#
#                if ret:
#                    returnResponse(Response(
#                        statusCode=200,
#                        properties={'Listen', listen}))
#                else:
#                    returnResponse(Response(statusCode=400))
#
#                return
#
#        if tunnelType == 'STREAM':
#            with self.__lock:
#                if listen not in self.__streamRelayTunnels:
#                    returnResponse(Response(statusCode=400))
#                    return
#
#                channel = self.__clients[request.remoteAddress] \
#                        .joinStream(self.__streamRelayTunnels[tunnel], request.connection, listen)
#
#                if channel is not None:
#                    returnResponse(Response(
#                        statusCode=200,
#                        properties={'Listen', channel}))
#                else:
#                    returnResponse(Response(statusCode=400))
#
#                return
#
#        returnResponse(Response(statusCode=400))
#
#    def onLeave(self, request, returnResponse):
#        tunnelType = request.getProperty('Type')
#        tunnel = None
#        listen = None
#        try:
#            tunnel = int(request.getProperty('Tunnel'))
#            listen = int(request.getProperty('Listen'))
#        except:
#            returnResponse(Response(statusCode=400))
#            return
#
#        remoteIp, remotePort = request.remoteAddress
#
#        if tunnelType == 'UDP':
#            with self.__lock:
#                if tunnel not in self.__udpRelayTunnels:
#                    returnResponse(Response(statusCode=400))
#                    return
#
#                ret = self.__clients[request.remoteAddress] \
#                        .leaveUdp(self.__udpRelayTunnels[tunnel], remoteIp, listen)
#
#                if ret:
#                    returnResponse(Response(statusCode=200))
#                else:
#                    returnResponse(Response(statusCode=400))
#
#                return
#
#        if tunnelType == 'STREAM':
#            with self.__lock:
#                if listen not in self.__streamRelayTunnels:
#                    returnResponse(Response(statusCode=400))
#                    return
#
#                ret = self.__clients[request.remoteAddress] \
#                        .leaveStream(self.__streamRelayTunnels[tunnel], request.connection, listen)
#
#                if ret:
#                    returnResponse(Response(statusCode=200))
#                else:
#                    returnResponse(Response(statusCode=400))
#
#                return
#
#        returnResponse(Response(statusCode=400))
#
#    # ----------------------------------------------------------------------
#    # RSP Stream Handler
#    # ----------------------------------------------------------------------
#
#    def onStream(self, stream):
#        with self.__lock:
#            for channel in self.__streamRelayTunnels:
#                if stream.channel == channel:
#                    self.__streamRelayTunnels[channel].broadcast(stream)
