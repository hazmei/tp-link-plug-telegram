import pyHS100
import logging
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# available commands: state, state(), is_on, turn_on(),
#			turn_off(), on_since(), state_information

FILENAME = 'logs/output.log'
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',filename=FILENAME,level=logging.INFO)

logger.setLevel(logging.INFO) #change to logging.DEBUG or logging.INFO or logging.CRITICAL

t_TOKEN = "XXX"
t_CHATID = XXX

plug_LIGHT = "xxx.xxx.xxx.xxx"
plug_DESKTOP = "xxx.xxx.xxx.xxx"

p_light = pyHS100.SmartPlug(plug_LIGHT)
p_desktop = pyHS100.SmartPlug(plug_DESKTOP)

light_name = ['light','living room','living room light']
desk_name = ['desk','desktop']


def flip_state(p_obj):
    if p_obj.state == 'ON':
        p_obj.turn_off()
        return p_obj.state
    else:
        p_obj.turn_on()
        return p_obj.state


def check_auth(user_id):
    if user_id == t_CHATID:
        return True
    else:
        logger.info("User {} unauthorized".format(user_id))
        return False


def start_callback(bot, update):
    logger.debug("Start called: {}".format(update.message.chat_id))
    user_chat_id = update.message.chat_id

    if check_auth(user_chat_id):
        bot.send_chat_action(chat_id=user_chat_id, action=telegram.ChatAction.TYPING)
        bot.send_message(chat_id=user_chat_id, text='Hello {}. Below are the list of available smart plugs:\n1. *Light*\n2. *Desktop*'.format(update.message.from_user.first_name), parse_mode=telegram.ParseMode.MARKDOWN)


def help_callback(bot, update):
    logger.debug("Help called: {}".format(update.message.chat_id))
    user_chat_id = update.message.chat_id

    if check_auth(update.message.from_user.id):
        bot.send_chat_action(chat_id=user_chat_id, action=telegram.ChatAction.TYPING)
        bot.send_message(chat_id=user_chat_id, text='Here are the commands available:\n1. */start*\n2. */help*\n3. */status*\n4. */toggle* <device>', parse_mode=telegram.ParseMode.MARKDOWN)


def status_callback(bot, update):
    logger.debug("Status called: {}".format(update.message.chat_id))
    user_chat_id = update.message.chat_id

    if check_auth(user_chat_id):
        bot.send_chat_action(chat_id=user_chat_id, action=telegram.ChatAction.TYPING)

        comm_stat = 0
        light_state = "OFF"
        desk_state = "OFF"

        try:
            light_state = p_light.state
            comm_stat += 1

            desk_state = p_desktop.state

            bot.send_message(chat_id=user_chat_id, text='Living Room Light: *{}*\nDesktop: *{}*'.format(light_state, desk_state), parse_mode=telegram.ParseMode.MARKDOWN)
        except pyHS100.smartdevice.SmartDeviceException:
            if comm_stat == 0:
                bot.send_message(chat_id=user_chat_id, text='Unable to reach smart plug', parse_mode=telegram.ParseMode.MARKDOWN)
            elif comm_stat == 1:
                update.message.reply_text('Living Room Light: {}\nDesktop: Unable to reach'.format(light_state))
                bot.send_message(chat_id=user_chat_id, text='Living Room Light: *{}*\nDesktop: Unable to reach'.format(light_state), parse_mode=telegram.ParseMode.MARKDOWN)
        except Exception as e:
            bot.send_message(chat_id=user_chat_id, text='Exception occurred:\n*{}*'.format(e), parse_mode=telegram.ParseMode.MARKDOWN)


def toggle_callback(bot, update):
    logger.debug("Toggle called: {}".format(update.message.chat_id))
    user_chat_id = update.message.chat_id

    if check_auth(user_chat_id):
        bot.send_chat_action(chat_id=user_chat_id, action=telegram.ChatAction.TYPING)

        plug = update.message.text.replace("/toggle ","").lower()

        if "/toggle" in plug:
            bot.send_message(chat_id=user_chat_id, text='*/toggle* command missing device name', parse_mode=telegram.ParseMode.MARKDOWN)
            return

        # if plug in light_name:
        #     bot.send_message(chat_id=user_chat_id, text='Living Room Light plug toggle not allowed!', parse_mode=telegram.ParseMode.MARKDOWN)
        if plug in light_name:
        	bot.send_message(chat_id=user_chat_id, text='Living Room Light state: *{}*'.format(flip_state(p_light)), parse_mode=telegram.ParseMode.MARKDOWN)
        elif plug in desk_name:
            bot.send_message(chat_id=user_chat_id, text='Desktop plug state: *{}*'.format(flip_state(p_desktop)), parse_mode=telegram.ParseMode.MARKDOWN)
        else:
            logger.warn("Unknown /toggle request: {}".format(update.message))
            update.message.reply_text('Unknown smart plug')


def unknown(bot, update):
    logger.info("Unknown command from: {}".format(update.message.chat_id))
    if check_auth(update.message.from_user.id):
        bot.send_message(chat_id=user_chat_id, text='Sorry your request is not recognised. Type */help* to show the list of commands that I understand.', parse_mode=telegram.ParseMode.MARKDOWN)


def init_tUpdater():
    updater = Updater(t_TOKEN)

    dispatch = updater.dispatcher
    unknown_handler = MessageHandler(Filters.command, unknown)

    logger.debug("Adding dispatch to poll")

    dispatch.add_handler(CommandHandler('start', start_callback))
    dispatch.add_handler(CommandHandler('status', status_callback))
    dispatch.add_handler(CommandHandler('help', help_callback))
    dispatch.add_handler(CommandHandler('toggle', toggle_callback))
    dispatch.add_handler(unknown_handler)

    updater.start_polling()
    updater.idle()
    updater.stop()


def run():
    logger.info("Starting {}".format(__file__))
    init_tUpdater()


if __name__ == '__main__':
    run()
