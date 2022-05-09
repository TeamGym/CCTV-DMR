import logging
from typing import Dict, Optional, Tuple
from threading import Thread
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib, GstRtspServer

from dmr.util import ConfigHelper
from .RtspCctvSession import RtspCctvSession

l = logging.getLogger(__name__)
config = ConfigHelper().globalConfig
settings = ConfigHelper().globalConfig.globalSettings

class RtspPlayServer:
    def __init__(self,
            subRoute: str,
            connectionList: Dict[int, RtspCctvSession]):
        self.__subRoute = subRoute
        self.__connectionList = connectionList
        self.__clientList: Dict[GstRtspServer.RTSPMedia, GstRtspServer.RTSPClient] = {}
        self.__thread: Optional[Thread] = None
        self.__server: GstRtspServer.RTSPServer = None
        self.__mainLoop: GLib.MainLoop = None

    # ----------------------------------------------------------------------
    # Private Function
    # ----------------------------------------------------------------------

    def __createFactory(self,
            camId: int) -> Tuple[str, GstRtspServer.RTSPMediaFactory]:
        l.debug('create play media factory: camId={}'.format(camId))

        livePath = '/{}/{}'.format(self.__subRoute, camId)
        #liveLaunch = 'appsrc name=appsrc0 is-live=1 do-timestamp=1 block=1 format=time ! x264enc tune=zerolatency intra-refresh=1 ! rtph264pay pt=96 config-interval=5 name=pay0'
        liveLaunch = 'appsrc name=appsrc0 is-live=1 do-timestamp=1 block=1 format=time ! h264parse ! rtph264pay pt=96 config-interval=5 name=pay0'

        factory = GstRtspServer.RTSPMediaFactory()
        factory.set_launch(liveLaunch)
        factory.set_shared(True)
        #factory.set_latency(0)
        factory.set_transport_mode(GstRtspServer.RTSPTransportMode.PLAY)
        self.__server.get_mount_points().add_factory(livePath, factory)
        factory.connect('media-configure', self.__mediaConfigure, camId)

        return livePath, factory

    # ----------------------------------------------------------------------
    # Signal Callback
    # ----------------------------------------------------------------------

    def __mediaConfigure(self,
            factory: GstRtspServer.RTSPMediaFactory,
            media: GstRtspServer.RTSPMedia,
            camId: int):
        if camId in self.__connectionList:
            session = self.__connectionList[camId]
            media.set_reusable(True)
            if session.playerAppSrc is None:
                session.playerAppSrc = media.get_element().get_by_name_recurse_up('appsrc0')
                l.debug('set playerAppSrc (camId={})'.format(camId))
        else:
            l.info('could not find corresponding recorder (camId={})'.format(camId))

    def __clientClosed(self,
            client: GstRtspServer.RTSPClient,
            camId: int) -> None:
        l.info('client closed {}'.format(client.get_connection().get_ip()))
        if camId not in self.__connectionList:
            return

        session = self.__connectionList[camId]
        session.playerCount -= 1

        l.debug('session.playerCount={} (camId={})'.format(session.playerCount, camId))
        if session.playerCount <= 0:
            l.debug('remove player media factory (camId={})'.format(camId))
            session.playerMediaFactory.set_eos_shutdown(True)
            self.__server.get_mount_points().remove_factory(session.playPath)

            session.playPath = None
            session.playerMediaFactory = None
            session.playerAppSrc = None
            session.playerInitialized = False

    def __preDescribeRequest(self,
            client: GstRtspServer.RTSPClient,
            context: GstRtspServer.RTSPContext) -> None:
        l.info('pre-describe-request from {}'.format(client.get_connection().get_ip()))

        pathv = context.uri.decode_path_components()

        if pathv is None or pathv[1] != self.__subRoute:
            l.info('Invalid path: {}'.format(context.uri.get_request_uri()))
            return 400 # GstRTSPStatusCode.GST_RTSP_STS_BAD_REQUEST

        camId = -1
        try:
            camId = int(pathv[2])
        except ValueError:
            l.info('Invalid camId: {}'.format(camId))
            return 400 # GstRTSPStatusCode.GST_RTSP_STS_BAD_REQUEST

        if camId not in self.__connectionList:
            l.info('media not created (camId={})'.format(camId))
            return 400 # GstRTSPStatusCode.GST_RTSP_STS_BAD_REQUEST

        session = self.__connectionList[camId]

        if session.playerMediaFactory is None:
            path, factory = self.__createFactory(camId)
            session.playerMediaFactory = factory
            session.playPath = path

        client.connect('closed', self.__clientClosed, camId)
        session.playerCount += 1

        return 200 # GstRTSPStatusCode.GST_RTSP_STS_OK

    def __clientConnected(self,
            server: GstRtspServer.RTSPServer,
            client: GstRtspServer.RTSPClient) -> None:
        l.info('client-connected from {}'.format(client.get_connection().get_ip()))
        client.connect('pre-describe-request', self.__preDescribeRequest)

    # ----------------------------------------------------------------------
    # Public Function
    # ----------------------------------------------------------------------

    def start(self) -> None:
        assert self.__thread is None
        self.__thread = Thread(target=self.run)
        self.__thread.daemon = True
        self.__thread.start()

    def run(self) -> None:
        self.__mainLoop = GLib.MainLoop()
        GLib.threads_init()
        Gst.init(None)

        self.__server = GstRtspServer.RTSPServer()
        self.__server.set_service(str(settings.rtspPlayPort))
        self.__server.attach(None)
        self.__server.connect('client-connected', self.__clientConnected)

        l.info('Rtsp Relay Server Play Server start on {}'.format(settings.rtspPlayPort))
        self.__mainLoop.run()

    def stop(self) -> None:
        l.info('Rtsp Relay Server Play Server stop')
        self.__mainLoop.quit()

