import logging
import socket
from threading import Thread, RLock

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

l = logging.getLogger(__name__)
class UdpRelayTunnel(Thread):
    initialized = False

    RELAY_PIPELINE = \
                'udpsrc name=m_udpsrc' \
                ' ! multiudpsink name=m_multiudpsink'
    RECORD_PIPELINE = \
                'udpsrc name=m_udpsrc' \
                ' ! multiudpsink name=m_multiudpsink'

    def __init__(self, inBoundPort, outBoundPort=0, recordMode=False):
        super().__init__()
        self.__inBoundPort = inBoundPort
        self.__outBoundPort = outBoundPort
        self.__recordMode = recordMode
        self.__receivers = []

        self.__lock = RLock()

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
        else:
            return True

        l.debug('Pipeline stop')
        self.__loop.quit()

        return True

    def receiverExists(self, connection, listenPort):
        return (connection, listenPort) in self.__receivers

    def addReceiver(self, connection, listenPort):
        with self.__lock:
            if (connection, listenPort) in self.__receivers:
                return False

            ip = connection.sock.getpeername()[0]

            l.debug('add receiver ip={}, port={}'
                    .format(ip, listenPort))
            self.__receivers.append((connection, listenPort))
            self.__multiudpsink.emit('add', ip, listenPort)

            return True

        raise RuntimeError

    def removeReceiver(self, connection, listenPort):
        with self.__lock:
            ip = connection.sock.getpeername()[0]

            if (connection, listenPort) in self.__receivers:
                self.__receivers.remove((connection, listenPort))
                self.__multiudpsink.emit('remove', ip, listenPort)

                return True

        raise RuntimeError

    def removeConnection(self, connection):
        with self.__lock:
            ip = connection.sock.getpeername()[0]

            removed = filter(lambda arg: arg[0] == connection, self.__receivers)

            for item in removed:
                _, port = item

                self.__receivers.remove(item)
                self.__multiudpsink.emit('remove', ip, port)

        raise RuntimeError

    def stop(self):
        self.__pipeline.send_event(Gst.Event.new_eos())

    def run(self):
        if not UdpRelayTunnel.initialized:
            GLib.threads_init()
            Gst.init(None)

            UdpRelayTunnel.initialized = True

        self.__loop = GLib.MainLoop.new(None, False)

        if self.__recordMode:
            self.__pipeline = Gst.parse_launch(self.RECORD_PIPELINE)
        else:
            self.__pipeline = Gst.parse_launch(self.RELAY_PIPELINE)

        self.__udpsrc = self.__pipeline.get_by_name('m_udpsrc')
        self.__udpsrc.set_property('port', self.__inBoundPort)

        self.__multiudpsink = self.__pipeline.get_by_name('m_multiudpsink')
        self.__multiudpsink.set_property('bind-port', self.__outBoundPort)

        bus = self.__pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.__onBusMessage)

        l.debug('Pipeline playing')
        self.__pipeline.set_state(Gst.State.PLAYING)
        self.__loop.run()
