import logging
import threading
import socket

from dmr.util import ConfigHelper
from .TcpRelayClientThread import TcpRelayClientThread

l = logging.getLogger(__name__)
config = ConfigHelper().globalConfig
settings = config.globalSettings
class TcpRelayServer():
    def __init__(self):
        self.client_thread_dict = {}

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def run(self):
        l.info('Tcp Server start on {}'.format(settings.tcpPort))
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('', settings.tcpPort))
        self.server.listen(10)

        while True:
            (clientsocket, address) = self.server.accept()
            clientsocket.setblocking(True)
            l.info(f'connection from {address}')
            TcpRelayClientThread(clientsocket, address, self.client_thread_dict).start()

    def stop(self):
        l.info('Tcp Server stop')
        self.server.close()
