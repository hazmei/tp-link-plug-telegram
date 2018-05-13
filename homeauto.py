#!/usr/bin/python3
import logging
import sockets
import sys
import pyHS100

FILENAME = 'logs/output.log'
ENCRYPTION_KEY = '<insert same key as server.py here for socket data encryption/decryption>'

LIGHT_IP = "<ip address of smartplug 1>"
DESKTOP_IP = "<ip address of smartplug 1>"

LIGHT_OBJ = pyHS100.SmartPlug(LIGHT_IP)
DESKTOP_OBJ = pyHS100.SmartPlug(DESKTOP_IP)

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',filename=FILENAME,level=logging.INFO)
logger.setLevel(logging.DEBUG) #change to logging.DEBUG or logging.INFO or logging.CRITICAL


def socket_handler(sockObj):
    logger.debug("Starting server socket")

    try:
        sockObj.start_server()

        while True:
            logger.debug("Waiting to receive data")
            command = sockObj.receive_data()
            logger.debug("Command received: {}".format(command))

            if command == '' or command == None:
                logger.info("Client connection terminated")
                sockObj.restart_server()
            else:
                response = command_handler(command)
                sockObj.send_data(response)

    except KeyboardInterrupt:
        sockObj.terminate()


def command_handler(command):
    isDevice_desktop = False
    isDevice_light = False

    if 'desktop' in command:
        isDevice_desktop = True
    elif 'light' in command:
        isDevice_light = True

    if 'status' in command:
        if isDevice_light or isDevice_desktop:
            if isDevice_light:
                return 'Living Room light state: *{}*'.format(LIGHT_OBJ.state)
            else:
                return 'Desktop state: *{}*'.format(DESKTOP_OBJ.state)
        else:
            # get status for all
            try:
                light_state = LIGHT_OBJ.state
            except Exception as e:
                light_state = e

            try:
                desktop_state = DESKTOP_OBJ.state
            except Exception as e:
                desktop_state = e

            return "Living Room Light: *{}*\nDesktop: *{}*".format(light_state, desktop_state)
    elif 'on' in command:
        if isDevice_light:
            LIGHT_OBJ.turn_on()
            return 'Living Room light state: *{}*'.format(LIGHT_OBJ.state)
        else:
            DESKTOP_OBJ.turn_on()
            return 'Desktop state: *{}*'.format(DESKTOP_OBJ.state)
    elif 'off' in command:
        if isDevice_light:
            LIGHT_OBJ.turn_off()
            return 'Living Room light state: *{}*'.format(LIGHT_OBJ.state)
        else:
            DESKTOP_OBJ.turn_off()
            return 'Desktop state: *{}*'.format(DESKTOP_OBJ.state)


def run():
    logger.info("Starting {}".format(__file__))
    try:
        socketsObj = sockets.communication('0.0.0.0', '<Local port to listen to>', ENCRYPTION_KEY)
        socket_handler(socketsObj)
    except Exception as e:
        logger.critical("Exception on run() occurred: {}".format(e))
    finally:
        print("Terminating {}".format(__file__))
        sys.exit(0)


if __name__ == '__main__':
    run()
