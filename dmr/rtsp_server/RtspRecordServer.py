import logging
from threading import Thread
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib, GstRtspServer

from dmr.utils import ConfigHelper

l = logging.getLogger(__name__)
config = ConfigHelper().globalConfig
settings = config.globalSettings
class RtspRecordServer:
    def __init__(self,
            connectionList: Dict[int, RtspCctvSession]):
        self.__connectionList = connectionList
        self.__thread = None
        self.__server: GstRtspServer.RTSPServer = None
        self.__mainLoop: GLib.MainLoop = None

    # ----------------------------------------------------------------------
    # Private Functions
    # ----------------------------------------------------------------------

    def __createFactories(self):
        for camConfig in config.cameraConfigs:
            l.debug('create record factory: camId={}'.format(camConfig.camId))

            recordPath = '/record/{}'.format(camConfig.camId)

            factory = GstRtspServer.RTSPMediaFactory()
            factory.set_launch('rtph264depay name=depay0 ! fakesink')
            factory.set_latency(0)
            factory.set_transport_mode(GstRtspServer.RTSPTransportMode.RECORD)
            self.server.get_mount_points().add_factory(recordPath, factory)
            factory.connect('media-configure', self.__mediaConfigure, camId)
    
    def __mediaConfigure(self, factory, meia, camId):
        pad = media
            .get_element()
            .get_by_name_recurse_up('depay0')
            .get_static_pad('src')
        pad.add_probe(Gst.PadProbeType.BUFFER, self.bufferCallback, camId)
        # CAM에서 연결을 시도하면 __connectionList에 session생성 후 추가
        # 연결을 끊으면 __connectionList에서 session제거

    # ----------------------------------------------------------------------
    # Public Functions
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
        self.__server.set_service(settings.rtspRecordPort)
        self.__createFactories()
        # ...

        l.info('Rtsp Relay Server Record Server start on {}'.format(settings.rtspRecordPort))
        self.__mainLoop.run()

    def stop(self) -> None:
        l.info('Rtsp Relay Server Record Server stop')
        self.__mainLoop.quit()

