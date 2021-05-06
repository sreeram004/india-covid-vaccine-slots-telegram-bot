#!/usr/bin/env python
# pylint: disable=C0116
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, ForceReply
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

import db_operations

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

NUM_DAYS = 7
TOKEN = os.environ.get("BOT_TOKEN", "TOKEN-HERE")
DISTRICT, AGE, CHECK, WORK, BYE = range(5)
CHECK_MINTS = 1


def start(update: Update, _: CallbackContext) -> int:
    states = db_operations.StateDB().get_states()
    s = ""
    for state in states:
        s += f"{state['state_id']}. {state['state_name']}\n"

    update.message.reply_text(
        'Hi! My name is Vaccine Slot Bot. I will search and find COVID vaccine slots at your pincode\n'
        'Send /cancel to stop talking to me.\n\n'
        'Enter the state number from the list below \n\n'
        '{}'.format(s),
        reply_markup=ReplyKeyboardRemove(),
    )

    return DISTRICT


def district_list(update: Update, con: CallbackContext) -> int:
    user = update.message.from_user

    logger.info(update.message.chat_id)

    logger.info("State of %s: %s", user.first_name, update.message.text)

    state_id = int(update.message.text)
    states = db_operations.StateDB().get_states()
    state_name = [state["state_name"] for state in states if state["state_id"] == state_id]

    logger.info(f"I found state name as {state_name}")

    districts = db_operations.DistrictDB().get_districts(state_id=state_id)

    s = ""
    for state in districts:
        s += f"{state['district_id']}. {state['district_name']}\n"

    logger.info(s)

    update.message.reply_text(
        'Enter the district number from the list below \n\n'
        '{}'.format(s),
        reply_markup=ReplyKeyboardRemove(),
    )

    con.user_data["state_id"] = state_id
    con.user_data["state_name"] = state_name

    return AGE


def age(update: Update, con: CallbackContext) -> int:
    district_id = int(update.message.text)
    logger.info(f"District is {district_id}")

    state_id = con.user_data["state_id"]
    districts = db_operations.DistrictDB().get_districts(state_id)
    district_name = [dist["district_name"] for dist in districts if dist["district_id"] == district_id][0]

    logger.info(f"Found dist name as {district_name}")

    update.message.reply_text(
        f'Tell me your age.',
        reply_markup=ReplyKeyboardRemove()
    )

    con.user_data["district_id"] = district_id
    con.user_data["district_name"] = district_name

    return CHECK


def check(update: Update, con: CallbackContext) -> int:
    logger.info(f"Age is {update.message.text}")

    update.message.reply_text(
        f'Do you want me to check vaccine slot availability at {con.user_data["district_name"]} '
        f'district for {update.message.text}+ age every {CHECK_MINTS} minutes.?',
        reply_markup=ReplyKeyboardMarkup([["Yes", "No"]], one_time_keyboard=True),
    )

    con.user_data["age"] = int(update.message.text)

    return WORK


def do_work_or_quit(update: Update, con: CallbackContext) -> int:
    logger.info(f"Reply is {update.message.text}")

    if update.message.text == "No":
        return BYE

    update.message.reply_text(
        f'I will check every {CHECK_MINTS} minutes from now and notify if there is a slot availability.!'
        '\nSend /stop_bot to make me stop checking',
        reply_markup=ReplyKeyboardRemove()
    )

    logger.info(f"Chat id : {update.message.chat_id} - State : {con.user_data['state_id']} - "
                f"District : {con.user_data['district_id']}, Age : {con.user_data['age']}")

    status = db_operations.BotDB().insert(
        {
            "chat_id": update.message.chat_id,
            "state_id": con.user_data['state_id'],
            "state_name": con.user_data['state_name'],
            "district_id": con.user_data['district_id'],
            "district_name": con.user_data['district_name'],
            "age": con.user_data['age']
        }
    )

    logger.info(f"{status}")

    return ConversationHandler.END


def cancel(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye.!', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def stop_bot(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the checking", user.first_name)
    update.message.reply_text(
        'Bye.! I will not check slots from now.!', reply_markup=ReplyKeyboardRemove()
    )

    db_operations.BotDB().delete(chat_id=update.message.chat_id)

    return ConversationHandler.END


def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), CommandHandler("stop_bot", stop_bot)],
        states={
            DISTRICT: [MessageHandler(Filters.regex('\d+'), district_list)],
            AGE: [MessageHandler(Filters.regex('\d+'), age)],
            CHECK: [MessageHandler(Filters.regex('\d+'), check)],
            WORK: [MessageHandler(Filters.regex('^(Yes|No)$'), do_work_or_quit)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
