import signal
import logging

from .UdpRelayTunnel import UdpRelayTunnel
from dmr.util import Singleton

l = logging.getLogger(__name__)
config = ConfigHelper().globalConfig
settings = config.globalSettings
class DmrServer(metaclass=Singleton):
    def __init__(self):
        self.__udpRelayTunnels = {}

        self.__serverSocket = None

    def onSigInt(self, sig, frame) -> None:
        l.info('Stop DmrServer')

        self.__running = False
        self.__serverSocket.close()

    def run(self) -> None:
        signal.signal(signal.SIGINT, self.onSigInt)
        l.info('Start DmrServer on {}'.format(settings.serverPort))

        for cam in config.cameraConfigs:
            self.__udpRelayTunnels[cam.camId] = UdpRelayTunnel(cam.udpPort)

        self.__serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__serverSocket.bind(('', settings.tcpPort))
        self.__serverSocket.listen(10)
        self.__serverSocket.setblocking(True)

        while self.__running:
            (clientSocket, address) = self.__serverSocket.accept()
            l.info('Connected from {}'.format(clientSocket.getpeername()))

            self.__clients.append(RspConnection(
                endpointType=EndpointType.DMR,
                sock=clientSocket,
                requestHandlers={
                    Request.Method.GET_INFO: self.onGetInfo,
                    Request.Method.JOIN: self.onJoin}))

    # ----------------------------------------------------------------------
    # RSP Request Handler
    # ----------------------------------------------------------------------

    def onGetInfo(self, request, returnResponse):
        response = Response(statusCode=200)

        response.addProperty('CamList',
                ','.join([camera.camId for camera in config.cameraConfigs]))

        for camera in config.cameraConfigs:
            response.addProperty('Cam{}-Name'.format(camera.camId), camera.name)
            response.addProperty('Cam{}-UdpPort'.format(camera.camId), str(camera.udpPort))

        returnResponse(response)

    def onJoin(self, request, returnResponse):
        camId = None
        port = None
        try:
            camId = int(request.getProperty('CamId'))
            port = int(request.getProperty('Port'))
        except:
            pass

        if camId is None or port is None or camId not in self.__udpRelayTunnels:
            returnResponse(Response(statusCode=400))
            return

        self.__udpRelayTunnels[camId].addReceiver(request.remoteAddress)

        returnResponse(Response(statusCode=200))
