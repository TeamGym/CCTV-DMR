from typing import Dict
import logging
import threading
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib

from dmr.classes import Singleton
from dmr.util import ConfigHelper
from .RtspRecordServer import RtspRecordServer
from .RtspPlayServer import RtspPlayServer

l = logging.getLogger(__name__)

class RtspRelayServer(metaclass=Singleton):
    def __init__(self):
        self.__connectionList: Dict[int, Dict]  = {}
        self.__rtspRecordServer = RtspRecordServer('record', self.__connectionList)
        self.__rtspPlayServer = RtspPlayServer('live', self.__connectionList)

    def start(self) -> None:
        l.info('Rtsp Relay Server start')
        self.__rtspRecordServer.start()
        self.__rtspPlayServer.start()

    def stop(self) -> None:
        l.info('Rtsp Relay Server stop')
        self.__rtspRecordServer.stop()
        self.__rtspPlayServer.stop()

