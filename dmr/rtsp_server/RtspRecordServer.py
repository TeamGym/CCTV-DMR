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
settings = config.globalSettings

class RtspRecordServer:
    def __init__(self,
            subRoute: str,
            connectionList: Dict[int, RtspCctvSession]):
        self.__subRoute = subRoute
        self.__connectionList = connectionList
        self.__thread: Optional[Thread] = None
        self.__server: GstRtspServer.RTSPServer = None
        self.__mainLoop: GLib.MainLoop = None

        self.__frameCount = 0

    # ----------------------------------------------------------------------
    # Private Function
    # ----------------------------------------------------------------------

    def __pushBuffer(self,
            buf: Gst.Buffer,
            target: Gst.Element) -> None:
        clock = target.get_clock()
        timestamp = clock.get_internal_time() - target.get_base_time()
        ret, mapInfo = buf.map(Gst.MapFlags.READ)

        #duration = int(1 / 30 * 1e9)
        #frameTimestamp = self.__frameCount * duration
        #self.__frameCount += 1

        bufNew = Gst.Buffer.new_allocate(None, buf.get_size(), None)
        bufNew.fill(0, mapInfo.data)
        #bufNew.pts = Gst.CLOCK_TIME_NONE
        #bufNew.dts = Gst.CLOCK_TIME_NONE
        #bufNew.pts = frameTimestamp
        #bufNew.dts = frameTimestamp
        bufNew.pts = timestamp
        bufNew.dts = timestamp
        #bufNew.pts = buf.pts
        #bufNew.dts = buf.dts
        #bufNew.duration = Gst.CLOCK_TIME_NONE
        #bufNew.duration = duration
        bufNew.duration = buf.duration
        target.emit('push-buffer', bufNew)

        #l.debug('bufNew.pts={}'.format(buf.pts))

        #clock.unref()
        buf.unmap(mapInfo)

    def __createFactory(self,
            camId: int) -> Tuple[str, GstRtspServer.RTSPMediaFactory]:
        l.debug('create record media factory: camId={}'.format(camId))

        recordPath = '/{}/{}'.format(self.__subRoute, camId)
        #recordLaunch = 'rtph264depay ! h264parse ! avdec_h264 ! videoconvert name=m_videoconvert ! fakesink' # video/x-raw,width=640,height=480,framerate=30/1,format=I420,stream-format=byte-stream ! fakesink' #,chroma-site=mpeg2,colorimetry=2:4:16:1 ! fakesink'
        recordLaunch = 'rtph264depay name=depay0 ! fakesink'

        factory = GstRtspServer.RTSPMediaFactory()
        factory.set_launch(recordLaunch)
        factory.set_latency(0)
        factory.set_transport_mode(GstRtspServer.RTSPTransportMode.RECORD)
        self.__server.get_mount_points().add_factory(recordPath, factory)

        return recordPath, factory

    # ----------------------------------------------------------------------
    # Signal Callback
    # ----------------------------------------------------------------------

    def __bufferCallback(self,
            pad: Gst.Pad,
            info: Gst.PadProbeInfo,
            session: RtspCctvSession) -> Gst.PadProbeReturn:
        if session.playerAppSrc is not None:
            if not session.playerInitialized:
                l.debug('initialize player')
                caps = pad.get_current_caps().copy()
                #caps.set_value('stream-format', 'byte-stream')
                caps.set_value('profile', 'high')
                l.debug('recorder caps: {}'.format(caps.to_string()))
                session.playerAppSrc.set_caps(caps)
                self.__frameCount = 0
                session.playerInitialized = True

            self.__pushBuffer(info.get_buffer(), session.playerAppSrc)

        return Gst.PadProbeReturn.OK

    def __mediaConfigure(self,
            factory: GstRtspServer.RTSPMediaFactory,
            media: GstRtspServer.RTSPMedia,
            camId: int):
        mediaElement = media.get_element().get_by_name_recurse_up('depay0')
        #mediaElement = media.get_element().get_by_name_recurse_up('m_videoconvert')
        session = None
        if camId in self.__connectionList:
            session = self.__connectionList[camId]
        else:
            l.info('media not created (camId={})'.format(camId))
            return

        pad = mediaElement.get_static_pad('src')
        pad.add_probe(Gst.PadProbeType.BUFFER, self.__bufferCallback, session)

    def __clientClosed(self,
            client: GstRtspServer.RTSPClient,
            camId: int) -> None:
        l.info('client closed {}'.format(client.get_connection().get_ip()))
        if camId not in self.__connectionList:
            return

        session = self.__connectionList[camId]
        session.recorderCount -= 1

        l.debug('session.playerCount={} (camId={})'.format(session.playerCount, camId))
        if session.recorderCount <= 0:
            l.info('recorder disconnected. remove session (camId={})'.format(camId))
            if session.playerMediaFactory is not None:
                session.playerMediaFactory.set_eos_shutdown(True)
                self.__server.get_mount_points().remove_factory(session.playPath)
            session.recorderMediaFactory.set_eos_shutdown(True)
            self.__server.get_mount_points().remove_factory(session.recordPath)
            del self.__connectionList[camId]

    def __optionsRequest(self,
            client: GstRtspServer.RTSPClient,
            context: GstRtspServer.RTSPContext) -> None:
        l.info('options-request from {} uri={}'
                .format(client.get_connection().get_ip(), context.uri.get_request_uri()))

        pathv = context.uri.decode_path_components()

        if pathv is None or pathv[1] != self.__subRoute:
            l.info('Invalid path: {}'.format(context.uri.get_request_uri()))
            client.close()
            return

        camId = -1
        try:
            camId = int(pathv[2])
        except ValueError:
            pass

        camIdExists = False
        for camConfig in config.cameraConfigs:
            if camConfig.camId == camId:
                camIdExists = True

        if not camIdExists:
            l.info('Invalid camId: {}'.format(camId))
            client.close()
            return

        session = None
        if camId not in self.__connectionList:
            path, factory = self.__createFactory(camId)
            session = RtspCctvSession(recorderMediaFactory=factory, recordPath=path)
            l.debug('(session created) session.playerInitialized = {}'.format(session.playerInitialized))
            self.__connectionList[camId] = session
            factory.connect('media-configure', self.__mediaConfigure, camId)
        else:
            session = self.__connectionList[camId]

        if session.recorderCount >= 1:
            l.info('There is a recorder already in the session (camId={})'.format(camId))
            client.close()
            return

        client.connect('closed', self.__clientClosed, camId)
        session.recorderCount += 1

    def __clientConnected(self,
            server: GstRtspServer.RTSPServer,
            client: GstRtspServer.RTSPClient) -> None:
        l.info('client-connected from {}'.format(client.get_connection().get_ip()))
        #client.connect('pre-describe-request', self.__preDescribeRequest)
        client.connect('options-request', self.__optionsRequest)

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
        self.__server.set_service(str(settings.rtspRecordPort))
        self.__server.attach(None)
        self.__server.connect('client-connected', self.__clientConnected)

        l.info('Rtsp Relay Server Record Server start on {}'.format(settings.rtspRecordPort))
        self.__mainLoop.run()

    def stop(self) -> None:
        l.info('Rtsp Relay Server Record Server stop')
        self.__mainLoop.quit()

