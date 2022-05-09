from dataclasses import dataclass
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GstRtspServer

@dataclass
class RtspCctvSession:
    recorderMediaFactory: GstRtspServer.RTSPMediaFactory
    recordPath: str
    recorderCount: int = 0

    playerMediaFactory: GstRtspServer.RTSPMediaFactory = None
    playPath: str = None
    playerCount: int = 0
    playerAppSrc: Gst.Element = None
    playerInitialized: bool = False

