import requests

def get_states_list():
    
    url = "https://cdn-api.co-vin.in/api/v2/admin/location/states"
    header = {"accept" : "application/json", "Accept-Language" : "hi_IN", \
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}
    response = requests.get(url, headers=header)
    
    d_states = dict()
    
    for state in response.json()["states"]:
        d_states[state["state_id"]] = state["state_name"]
    
    return d_states
