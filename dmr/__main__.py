from dmr.core import DmrServer
from dmr.utils import ConfigHelper
import logging

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(name)s %(levelname)s: %(message)s ',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO)
    ConfigHelper().setGlobalConfigPath('config/config.ini')
    dmr_server = DmrServer()
    dmr_server.run()

