# things to do:
#   - extend the telegram code to its own class
#   - multithread the processes to do the following:
#       1. listen for socket connection
#           - perform ping to client on an interval basis
#       2. listen for telegram messages
#   - add NLP (luis.ai maybe)

import logging
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

FILENAME = 'logs/output.log'
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',filename=FILENAME,level=logging.INFO)

logger.setLevel(logging.INFO) #change to logging.DEBUG or logging.INFO or logging.CRITICAL

t_TOKEN = "xxx"
t_CHATID = "xxx"


def check_auth(user_id):
    if user_id == t_CHATID:
        return True
    else:
        logger.warn("User {} unauthorized".format(user_id))
        return False


def start_callback(bot, update):
    logger.info("User {} requested start command".format(update.message.chat_id))
    user_chat_id = update.message.chat_id
    if check_auth(user_chat_id):
        bot.send_chat_action(chat_id=user_chat_id, action=telegram.ChatAction.TYPING)
        bot.send_message(chat_id=user_chat_id, text='Hello {}. I am your Personal Assistant.'.format(update.message.from_user.first_name), parse_mode=telegram.ParseMode.MARKDOWN)


def unknown(bot, update):
    logger.info("Unknown command from: {}".format(update.message.chat_id))
    user_chat_id = update.message.chat_id
    if check_auth(update.message.from_user.id):
        bot.send_chat_action(chat_id=user_chat_id, action=telegram.ChatAction.TYPING)
        bot.send_message(chat_id=user_chat_id, text='Sorry your request is not recognized. Type */help* to show the list of commands that i understand.', parse_mode=telegram.ParseMode.MARKDOWN)


def init_tUpdater():
    updater = Updater(t_TOKEN)

    dispatch = updater.dispatcher
    unknown_handler = MessageHandler(Filters.command, unknown)
    logger.debug("Adding dispatch to poll")

    dispatch.add_handler(CommandHandler('start', start_callback))
    dispatch.add_handler(unknown_handler)

    updater.start_polling()
    updater.idle()
    updater.stop()


def run():
    logger.info("Starting {}".format(__file__))
    init_tUpdater()


if __name__ == '__main__':
    run()
