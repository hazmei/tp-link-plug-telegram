# NOTE: This is for smarthome gateway
# Things to do:
#	- socket for communication between (This will be the client establishing to server serve.hazmei.tk)
#	- fork for sending commands to smartplugs
#	- 1 method for just checking connection
import logging
import sockets
import sys

FILENAME = 'logs/output.log'
ENCRYPTION_KEY = 'thisisthekey'

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',filename=FILENAME,level=logging.INFO)
logger.setLevel(logging.INFO) #change to logging.DEBUG or logging.INFO or logging.CRITICAL

def socketHandler(sockObj):
    print("Starting Server Socket")
    sockObj.start_server()
    print("Server started")

    data = "something"
    sockObj.send_data(data)
    print("Data sent!: {}".format(data))

    while True:
      try:
          response = sockObj.receive_data()
          print("Response: {}".format(response))
          if response == '' or response == None:
              print("Connection died")
              print("Insanity check: {}".format(sockObj.isAlive()))
              sockObj.restart_client()
              sockObj.send_data(sockObj.send_data())
      except KeyboardInterrupt:
          print("Terminating {}".format(__file__))
          sockObj.terminate()
          break


#figure out what's the authentication gonna be like
def auth(sockObj):
	return False

def run():
    logger.info("Starting {}".format(__file__))
    try:
    	socketsObj = sockets.communication('localhost',8082,ENCRYPTION_KEY)
    	socketHandler(socketsObj)
    except Exception as e:
    	logger.critical("Exception on run() occurred: {}".format(e))
    finally:
    	sys.exit(0)

if __name__ == '__main__':
    run()
