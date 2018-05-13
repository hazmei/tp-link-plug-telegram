#!/usr/bin/python3
# Note: Only launch client socket on command request
import sys
import logging
import sockets
import conversation
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from functools import wraps

FILENAME = 'logs/output.log'
ENCRYPTION_KEY = 'xxx'

LUIS_APPID = '<insert luis.ai appid here>'
LUIS_APPKEY = '<insert luis.ai appkey here>'

TOKEN = "<insert telegram here>"
LIST_OF_ADMINS = [<'insert approved lists of telegram chatid here here'>]

SOCKET_OBJ = sockets.communication('localhost',8082,ENCRYPTION_KEY)
CONVERSE = conversation.luis(LUIS_APPID, LUIS_APPKEY)

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',filename=FILENAME,level=logging.INFO)

logger.setLevel(logging.DEBUG) #change to logging.DEBUG or logging.INFO or logging.CRITICAL

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
            logger.warn('Unauthorized access denied for {}({}). Message: "{}"'.format(update.message.from_user.first_name, user_id, update.message.text))
            return
        return func(bot, update, *args, **kwargs)
    return wrapped


@restricted
def start_handler(bot, update):
    logger.debug("start_handler triggered: {}({})".format(update.message.from_user.first_name, update.message.chat_id))
    print("start_handler triggered")

    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=update.message.chat_id, text='Hello {}. Below are the list of available smart plugs:\n1. *Light*\n2. *Desktop*'.format(update.message.from_user.first_name), parse_mode=telegram.ParseMode.MARKDOWN)


@restricted
def help_handler(bot, update):
    logger.debug("help_handler triggered: {}({})".format(update.message.from_user.first_name, update.message.chat_id))
    print("help_handler triggered")

    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=update.message.chat_id, text='Here are the commands available:\n1. */start*\n2. */help*\n3. */status*\n4. */toggle* <device>', parse_mode=telegram.ParseMode.MARKDOWN)


# any msg that does not uses the telegram command handle eg. /start will trigger this method
# calls msg_handler to call luis api and resolve into proper commands
@restricted
def conversation_handler(bot, update):
    logger.debug("conversation_handler triggered: {}({})".format(update.message.from_user.first_name, update.message.chat_id))
    print("conversation_handler triggered")

    msg = update.message.text
    logger.debug("Message from {}: {}".format(update.message.from_user.first_name, msg))
    msg_handler(msg)


# resolve msg into proper commands
# if commands includes retrieving / switching smart plug, open socket to send commands to gateway
# then return status back to conversation_handler to update the user
def msg_handler(msg):
    response = CONVERSE.query(msg)
    print(CONVERSE.extract_commands(response))


# opens command and sends it over to the gateway
def socketHandler(command):
    logger.debug("Starting Client Socket")
    SOCKET_OBJ.start_client()
    logger.debug("Client started")

    data = "something"
    SOCKET_OBJ.send_data(data)
    print("Data sent!: {}".format(data))

    while True:
        try:
            response = SOCKET_OBJ.receive_data()
            print("Response: {}".format(response))
            if response == '' or response == None:
                print("Connection died")
                print("Insanity check: {}".format(SOCKET_OBJ.isAlive()))
                SOCKET_OBJ.restart_client()
                SOCKET_OBJ.send_data(SOCKET_OBJ.send_data())
        except KeyboardInterrupt:
            logger.info("Terminating {}".format(__file__))
            SOCKET_OBJ.terminate()
            break


def sock_auth():
    print()

def initialize_tbot(updater):
    dispatch = updater.dispatcher

    dispatch.add_handler(CommandHandler("start", start_handler))
    dispatch.add_handler(CommandHandler("help", help_handler))
    dispatch.add_handler(MessageHandler(Filters.text, conversation_handler))


def run():
    updater = Updater(TOKEN)
    initialize_tbot(updater)

    # starts the bot
    updater.start_polling()

    # runs the bot until the process receives SIGINT, SIGTERM or SIGABRT
    # start_polling() is non-blocking and will stop the bot gracefully
    updater.idle() # not necessary since our socket going to run forever
    updater.stop()
    # only on command
    # try:
    #     socketHandler(socketsObj, commands)
    # except Exception as e:
    #     print("Exception on run() occurred: {}".format(e))


if __name__ == "__main__":
    logger.info("Running {}".format(__file__))
    run()
    logger.info("Terminating {}".format(__file__))