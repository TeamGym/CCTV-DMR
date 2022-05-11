import logging
import socket
from threading import Thread

from dmr.rsp import RspConnection, EndpointType, Request, Response, Stream
from dmr.classes import Singleton
from dmr.util import ConfigHelper

l = logging.getLogger(__name__)
config = ConfigHelper().globalConfig
settings = config.globalSettings
class TcpRelayServer(metaclass=Singleton):
    def __init__(self):
        self.__thread = None
        self.__server = None
        self.__running = True
        self.__clients = []

    def __onGetInfo(self, request, returnResponse):
        response = Response(
                statusCode=200,
                statusMessage='OK')

        response.addProperty('CamList',
                ','.join([camera.camId for camera in config.cameraConfigs]))

        for camera in config.cameraConfigs:
            response.addProperty('Cam{}-Name'.format(camera.camId), camera.name)
            response.addProperty('Cam{}-UdpPort'.format(camera.camId), str(camera.udpPort))

        returnResponse(response)

    def __onControlPTZ(self, stream):
        print('control ptz: pan={}, tilt={}, zoom={}'.format(
            stream.data.pan,
            stream.data.tilt,
            stream.data.zoom))

    def start(self):
        assert self.__thread is None
        self.__thread = Thread(target=self.run)
        self.__thread.daemon = True
        self.__thread.start()

    def run(self):
        l.info('TCP Server start on {}'.format(settings.tcpPort))
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.bind(('', settings.tcpPort))
        self.__server.listen(10)
        self.__server.setblocking(True)

        while self.__running:
            (clientsocket, address) = self.__server.accept()
            l.info('TCP Connection from {}'.format(address))
            self.__clients.append(RspConnection(
                endpointType=EndpointType.DMR,
                sock=clientsocket,
                requestHandlers={
                    Request.Method.GET_INFO: self.__onGetInfo}))

    def stop(self):
        l.info('TCP Server stop')
        self.__running = False
        self.__server.shutdown(socket.SHUT_RDWR) # not tested
        self.__server.close()
