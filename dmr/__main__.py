from dmr.util import ConfigHelper
ConfigHelper().setGlobalConfigPath('config.json')
from dmr.core import DmrServer
import logging

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(name)s %(levelname)s: %(message)s ',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.DEBUG)
    dmr_server = DmrServer()
    dmr_server.run()

