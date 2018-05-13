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
ENCRYPTION_KEY = '<insert same key as homeauto.py here for socket data encryption/decryption>'

LUIS_APPID = '<luis.ai appid>'
LUIS_APPKEY = '<luis.ai appkey>'

TOKEN = "<telegram bot token>"
LIST_OF_ADMINS = ['<list of approved telegram user to chat with>']

SOCKET_OBJ = sockets.communication('<server ip/domain to connect>', '<server port to connect>', ENCRYPTION_KEY)
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

    msg = "Hey {}! You can request for status, turn on and off the available smart plugs below.\n- *Desktop*\n- *Living room light*\n\nJust converse to me normally and I will be able to understand your requests.".format(update.message.from_user.first_name)

    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)


@restricted
def help_handler(bot, update):
    logger.debug("help_handler triggered: {}({})".format(update.message.from_user.first_name, update.message.chat_id))

    msg = "Hey {}! You can request for status, turn on and off the available smart plugs below.\n- *Desktop*\n- *Living room light*\n\nJust converse to me normally and I will be able to understand your requests.".format(update.message.from_user.first_name)
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)


@restricted
def conversation_handler(bot, update):
    logger.debug("conversation_handler triggered: {}({})".format(update.message.from_user.first_name, update.message.chat_id))

    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    msg = update.message.text
    logger.debug("Message from {}: \"{}\"".format(update.message.from_user.first_name, msg))
    try:
        output = msg_handler(msg)
    except:
        output = "Sorry, I am unable to access the home gateway at the moment. Please try again later."

    if output == None:
        output = "Sorry I do not understand your request."
    elif output == 'start':
        output = "Hey {}! You can request for status, turn on and off the available smart plugs below.\n- *Desktop*\n- *Living room light*\n\nJust converse to me normally and I will be able to understand your requests.".format(update.message.from_user.first_name)

    try:
        bot.send_message(chat_id=update.message.chat_id, text=output, parse_mode=telegram.ParseMode.MARKDOWN)
    except:
        return


def msg_handler(msg):
    response = CONVERSE.query(msg)
    commands = CONVERSE.extract_commands(response)
    logger.info("luis.ai api response: {}".format(commands))

    if commands['command'] == None:
        return None
    elif commands['command'] == 'greetings':
        return "start"
    elif commands['command'] == 'status':
        try:
            return socket_handler("{} {}".format(commands['command'], commands['device']))
        except:
            return socket_handler("status all")
    elif commands['command'] == 'on':
        return socket_handler("{} {}".format(commands['command'], commands['device']))
    elif commands['command'] == 'off':
        return socket_handler("{} {}".format(commands['command'], commands['device']))


def socket_handler(command):    
    logger.debug("Starting client socket")
    SOCKET_OBJ.start_client()
    logger.debug("Client started")
    logger.debug("client data to send: {}".format(command))

    SOCKET_OBJ.send_data(command)

    response = SOCKET_OBJ.receive_data()
    logger.debug("data received: {}".format(response))

    if response == '' or response == None:
        logger.warn("Gateway closed the connection")
    
    SOCKET_OBJ.terminate()
    return response


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
    updater.idle()
    updater.stop()


if __name__ == "__main__":
    logger.info("Running {}".format(__file__))
    run()
    logger.info("Terminating {}".format(__file__))