# NOTE: This is for smarthome gateway
# Things to do:
#	- socket for communication between (This will be the client establishing to server serve.hazmei.tk)
#	- fork for sending commands to smartplugs
#	- 1 method for just checking connection
import logging
import sockets
import os

FILENAME = 'logs/output.log'
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',filename=FILENAME,level=logging.INFO)

logger.setLevel(logging.INFO) #change to logging.DEBUG or logging.INFO or logging.CRITICAL


def run():
    logger.info("Starting {}".format(__file__))
    socketsObj = sockets.communication('localhost',8088)


if __name__ == '__main__':
    run()
