from db_operations import BotDB
import datetime
import requests
import telegram
import time
import logging
import os
import pytz

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

CHECK_MINTS = int(os.environ.get("CHECK_DELAY", 1))


class Poller:
    def __init__(self, num_days=1, wait=15):
        self.db = BotDB()
        self.NUM_DAYS = num_days
        self.wait = wait
        self.bot = telegram.Bot(token=os.environ.get("BOT_TOKEN"))

        self.API_URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict?district_id={" \
                       "0}&date={1} "

    def __iter_chat_ids(self):
        data = self.db.get_all_data()
        for item in data:
            yield item["chat_id"], item["district_id"], item["district_name"], item["age"]

    @staticmethod
    def __parse_response(data, age):

        d_parsed_data = {}

        if len(data["sessions"]) == 0:
            return {}

        for session in data["sessions"]:

            if age >= int(session["min_age_limit"]):
                d_parsed_data[session["name"]] = {
                    "capacity": session["available_capacity"],
                    "fee": session["fee"],
                    "vaccine": session["vaccine"],
                    "slots": " ".join(session["slots"])
                }
        return d_parsed_data

    def __extract_info(self, district, age):

        time_zone = pytz.timezone("Asia/Calcutta")
        base = time_zone.localize(datetime.datetime.today())
        if base.hour >= 18:
            logger.info("Time is now past 6PM. Will check slots for next day")
            base += datetime.timedelta(days=1)
            
        l_next_NUM_DAYS_days = \
            [base + datetime.timedelta(days=x) for x in range(self.NUM_DAYS)]

        d_details = {}
        for date in l_next_NUM_DAYS_days:
            s_date = date.strftime("%d-%m-%Y")
            url = self.API_URL.format(district, s_date)
            header = {"accept": "application/json", "Accept-Language": "hi_IN",
                      "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                    "Chrome/90.0.4430.93 Safari/537.36"}
            response = requests.get(url, headers=header)
            if response.ok:
                data = response.json()
                d_details[date.strftime("%d-%B-%Y")] = self.__parse_response(data, age)

        return d_details

    def __build_message(self, district, details, force=False):

        msg_yes = f"You have a vaccine slot now available at {district} district.!!!\nSee Details below.\n"
        msg_no = f"You don't have a vaccine slot now available at {district} district.!!!\n\n"
                 
        if not force:
            msg_no += "I will check again in {self.wait} minutes\n"

        available = False
        for date, data in details.items():
            if len(data) != 0:
                available = True
                msg_yes += f"\nDate : {date}\n\n"
                for location, info in data.items():
                    txt = f'Location : {location}\nCapacity : {info["capacity"]}\nVaccine : {info["vaccine"]}\n' \
                          f'Fee : {info["fee"]}\nSlots : {info["slots"]}\n\n'
                    msg_yes += txt

        if not available:
            return False, msg_no

        return True, msg_yes

    def send(self, msg, chat_id):
        """
        Send a message to a telegram user specified on chatId
        chat_id must be a number!
        """
        self.bot.sendMessage(chat_id=chat_id, text=msg)
        
    def _send_notification(self, msg, chat_id):
        
        l_msg = [msg[i:i + 4000] for i in range(0, len(msg), 4000)]
        for m in l_msg:
            self.send(m, chat_id)
            
            
    def notify_one_user(self, district, age, district_name, chat_id,
                        force=False):
        
        details = self.__extract_info(district, age)
        flag, msg = self.__build_message(district_name, details, force=force)
        
        if force:
            logger.info(f"Notication will be send forcefully to {chat_id} at this time")
            self._send_notification(msg, chat_id)
            return
        
        if os.environ.get("RUN_ENV", "DEV") == "DEV":
            logger.info(f"Notification will be send to {chat_id} at this time")
            self._send_notification(msg, chat_id)
        if os.environ.get("RUN_ENV", "DEV") == "PROD":
            if flag:
                logger.info(f"Notification will be send to {chat_id} at this time")
                self._send_notification(msg, chat_id)
            else:
                logger.info(f"Notification will not be send to {chat_id} at this time")
                            
    def check_in_cowin(self):
        
        _iter = self.__iter_chat_ids()

        for chat_id, district, district_name, age in _iter:
            self.notify_one_user(district, age, district_name, chat_id)
                          

def do_polling():
    poller = Poller(num_days=1, wait=CHECK_MINTS)
    while True:
        logger.info("Wokeup.!")
        poller.check_in_cowin()
        logger.info("Going to sleep.!")
        time.sleep(CHECK_MINTS * 60)
        
if __name__ == "__main__":
    do_polling()