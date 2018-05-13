# things to do:
#   - extend the telegram code to its own class
#   - multithread the processes to do the following:
#       1. listen for socket connection
#           - perform ping to client on an interval basis
#       2. listen for telegram messages
#   - add NLP (luis.ai maybe)

import sys
import sockets
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from functools import wraps

ENCRYPTION_KEY = 'xxx'
TOKEN = "<telegram bot token here>"
LIST_OF_ADMINS = [xxx]

def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        # extract user_id from arbitrary update
        try:
            user_id = update.message.from_user.id
        except (NameError, AttributeError):
            try:
                user_id = update.inline_query.from_user.id
            except (NameError, AttributeError):
                try:
                    user_id = update.chosen_inline_result.from_user.id
                except (NameError, AttributeError):
                    try:
                        user_id = update.callback_query.from_user.id
                    except (NameError, AttributeError):
                        logger.error('No user_id available in update.')
                        return
        if user_id not in LIST_OF_ADMINS:
            print('Unauthorized access denied for {}.'.format(user_id))
            return
        return func(bot, update, *args, **kwargs)
    return wrapped


@restricted
def start_handler(bot, update):
    print("start_handler triggered")


@restricted
def help_handler(bot, update):
    print("help_handler triggered")


@restricted
def conversation_handler(bot, update):
    print("conversation_handler triggered")


def socketHandler(sockObj):
    logger.debug("Starting Client Socket")
    sockObj.start_client()
    logger.debug("Client started")

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
            logger.info("Terminating {}".format(__file__))
            sockObj.terminate()
            break


def initialize_tbot(updater):
    dispatch = updater.dispatcher

    dispatch.add_handler(CommandHandler("start", start_handler))
    dispatch.add_handler(CommandHandler("help", help_handler))
    dispatch.add_handler(MessageHandler(Filters.text, conversation_handler))


def run():
    print("Starting run")
    socketsObj = sockets.communication('localhost',8082,ENCRYPTION_KEY)

    updater = Updater(TOKEN)
    # initialize_tbot(updater)

    # starts the bot
    # updater.start_polling()

    # runs the bot until the process receives SIGINT, SIGTERM or SIGABRT
    # start_polling() is non-blocking and will stop the bot gracefully
    # updater.idle() # not necessary since our socket going to run forever

    try:
        socketHandler(socketsObj)
    except Exception as e:
        print("Exception on run() occurred: {}".format(e))
    finally:
        sys.exit(0)


if __name__ == "__main__":
    print("Running {}".format(__file__))
    run()
    print("Terminating {}".format(__file__))