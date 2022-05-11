import logging
from typing import Dict, Optional, Tuple
from threading import Thread
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

from dmr.util import ConfigHelper

l = logging.getLogger(__name__)
config = ConfigHelper().globalConfig
settings = config.globalSettings

class StreamingServer:
    def __init__(self):
        self.__thread: Optional[Thread] = None

        self.__frameCount = 0

    def start(self) -> None:
        assert self.__thread is None
        self.__thread = Thread(target=self.run)
        self.__thread.daemon = True
        self.__thread.start()

   #def __bufferCallback(self,
   #        pad: Gst.Pad,
   #        info: Gst.PadProbeInfo) -> None:

   #    l.debug('get buffer, size: {}'.format(info.get_buffer().get_size()))

   #    return Gst.PadProbeReturn.OK

    def run(self) -> None:
        GLib.threads_init()
        Gst.init(None)

        pipeline = Gst.parse_launch('udpsrc name=m_udpsrc ! udpsink name=m_udpsink')

        udpsrc = pipeline.get_by_name('m_udpsrc')
        udpsrc.set_property('port', 50500)

        #udpsrcPad = udpsrc.get_static_pad('src')
        #udpsrcPad.add_probe(Gst.PadProbeType.BUFFER, self.__bufferCallback)

        udpsink = pipeline.get_by_name('m_udpsink')
        udpsink.set_property('host', '127.0.0.1')
        udpsink.set_property('port', 50501)

        l.info('pipeline playing')
        pipeline.set_state(Gst.State.PLAYING)

        bus = pipeline.get_bus()
        while True:
            msg = bus.timed_pop_filtered(10000, Gst.MessageType.ERROR | Gst.MessageType.EOS)

            if msg:
                l.info('msg: ' + msg)


        l.info('pipeline terminate')
        pipeline.set_state(Gst.State.NULL)

    def stop(self) -> None:
        pass
