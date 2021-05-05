from db_operations import BotDB
import datetime
import requests

db = BotDB()

db._insert({"chat_id": 100, "district": 511, "age_group": 45})

class Poller:
    def __init__(self, num_days=3):
        self.db = BotDB()
        self.NUM_DAYS = num_days
        
        self.API_URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict?district_id={0}&date={1}"
    
    def __iter_chat_ids(self):
        data = self.db._get_all_data()
        for item in data:
            yield item["chat_id"], item["district"], item["age_group"]
            
        
    def __parse_reponse(self, data, age):
        
        d_parsed_data = {}
        
        if len(data["sessions"]) == 0:
            return {}
        
        for session in data["sessions"]:
            # slots = " ".join(session["slots"])
            # print(slots)
            if age >= int(session["min_age_limit"]):
                d_parsed_data[session["name"]] = {
                    "capacity": session["available_capacity"],
                    "fee": session["fee"],
                    "vaccine": session["vaccine"]
                }
        return d_parsed_data
            
        
    def __extract_info(self, district, age):
        
        base = datetime.datetime.today()
        l_next_NUM_DAYS_days = \
            [base + datetime.timedelta(days=x) for x in range(self.NUM_DAYS)]
        
        d_details = {}
        for date in l_next_NUM_DAYS_days:
            s_date = date.strftime("%d-%m-%Y")
            url = self.API_URL.format(district, s_date)
            header = {"accept" : "application/json", "Accept-Language" : "hi_IN", \
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}
            response = requests.get(url, headers=header)
            if response.ok:
                data = response.json()
                d_details[date.strftime("%d-%B-%Y")] = self.__parse_reponse(data, age)
                
        return d_details
                
        
        
            
    def _check_in_cowin(self):
        
        _iter = self.__iter_chat_ids()
        
        for chat_id, district, age in _iter:
            details = self.__extract_info(district, age)
            print(details)
        
        
x = Poller(1)._check_in_cowin()
print(x)