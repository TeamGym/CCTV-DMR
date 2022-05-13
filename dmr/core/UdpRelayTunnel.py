import logging
import socket
from threading import Thread

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

l = logging.getLogger(__name__)
class UdpRelayTunnel(Thread):
    def __init__(self, inBoundPort, outBoundPort=0):
        self.__inBoundPort = inBoundPort
        self.__outBoundPort = outBoundPort
        self.__receivers = []

        self.__loop = None
        self.__pipeline = None
        self.__udpsink = None
        self.__multiudpsink = None

    def __onBusMessage(self, bus, msg):
        if msg.type == Gst.MessageType.EOS:
            l.info('End of stream (port={})'.format(self.__inBoundPort))
        elif msg.type == Gst.MessageType.ERROR:
            err, debug = msg.parse_error()
            l.info('Error (port={}) {}: {}'.format(self.__inBoundPort, err, debug))

        l.debug('Pipeline stop')
        self.__loop.quit()

        return True

    def receiverExists(self, remote):
        return remote in self.__receivers

    def addReceiver(self, remote):
        assert remote not in self.__receivers

        host, port = remote

        self.__receivers.append(remote)
        self.__multiudpsink.emit('add', host, port)

    def removeReceiver(self, remote):
        if remote in self.__receivers:
            host, port = remote

            self.__receivers.remove(remote)
            self.__multiudpsink.emit('remove', host, port)

    def stop(self):
        self.__pipeline.send_event(Gst.Event.new_eos())

    def run(self):
        GLib.threads_init()
        Gst.init(None)
        self.__loop = GLib.MainLoop.new(None, False)

        self.__pipeline = Gst.parse_launch('udpsrc name=m_udpsrc ! multiudpsink name=m_multiudpsink')

        self.__udpsrc = self.__pipeline.get_by_name('m_udpsrc')
        self.__udpsrc.set_property('port', self.__inBoundPort)

        self.__multiudpsink = pipeline.get_by_name('m_multiudpsink')
        self.__multiudpsink.set_property('bind-port', self.__outBoundPort)

        bus = self.__pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.__onBusMessage)

        l.debug('Pipeline playing')
        self.__pipeline.set_state(Gst.State.PLAYING)
        self.__loop.run()
