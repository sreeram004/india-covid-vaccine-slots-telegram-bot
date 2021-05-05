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
import requests
import os
import datetime
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, ForceReply
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
import utils

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

NUM_DAYS = 7
TOKEN = os.environ.get("BOT_TOKEN", "TOKEN-HERE")
STATECODE, BYE = range(2)

def start(update: Update, _: CallbackContext) -> int:

    states = utils.get_states_list()
    s = ""
    for _id, state in states.items():
        s = s.join(f"\n{_id}.{state}")

    logger.info(f"States are {s}")
    update.message.reply_text(
        'Hi! My name is Vaccine Slot Bot. I will search and find COVID vaccine slots at your pincode\n'
        'Send /cancel to stop talking to me.\n\n'
        'Enter the state number from the list below \n\n'
        f'{s}',
        reply_markup=ForceReply(),
    )

    return STATECODE


def extract_available_dates(pin_code):

    l_slots_data = {}

    URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={0}&date={1}"

    base = datetime.datetime.today()
    l_next_NUM_DAYS_days = [base + datetime.timedelta(days=x) for x in range(NUM_DAYS)]

    for date in l_next_NUM_DAYS_days:
        
        s_date = date.strftime("%d-%m-%Y")
        response = requests.get(URL.format(pin_code, s_date))
        if response.ok:
            data = response.json()
            if data["centers"]:
                logger.info("You can book vaccine slots on {}".format(s_date))
                logger.info(data["centers"][0])
                l_slots_data[date] = True
            else:
                logger.info("No available slots on {}".format(s_date))
                l_slots_data[date]= False
        else:
            logger.error("API call failed.!")
            l_slots_data[date] = False


    l_dates = []
    for key, val in l_slots_data.items():
        if val is True:
            l_dates.append(key.strftime("%d-%B-%Y"))

    return ", ".join(l_dates)

def state_list(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    
    logger.info(update.message.chat_id)
    
    logger.info("State of %s: %s", user.first_name, update.message.text)

    update.message.reply_text(
        f'Please wait while I search......', reply_markup=None
    )

    pin_code = update.message.text
    s_dates = extract_available_dates(pin_code=pin_code)

    if len(s_dates) > 0:   
        update.message.reply_text(
            f'At Pincode {pin_code}, You can book slots on these days : {s_dates}',
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        update.message.reply_text(
            f'No Slots Availabe at {pin_code} for next {NUM_DAYS} days',
            reply_markup=ReplyKeyboardRemove(),
        )

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
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye.!', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), CommandHandler("stop_bot", stop_bot)],
        states={
            STATECODE: [MessageHandler(Filters.regex('\d+'), state_list)],
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