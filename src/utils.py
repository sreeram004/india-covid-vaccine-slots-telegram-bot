import requests
from tinydb import TinyDB, Query


def get_states_list():
    url = "https://cdn-api.co-vin.in/api/v2/admin/location/states"
    header = {"accept": "application/json", "Accept-Language": "hi_IN", \
              "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/90.0.4430.93 Safari/537.36"}
    response = requests.get(url, headers=header)

    d_states = dict()

    for state in response.json()["states"]:
        d_states[state["state_id"]] = state["state_name"]

    return d_states


states = get_states_list()

def get_district_list(state):

    url = "https://cdn-api.co-vin.in/api/v2/admin/location/districts/{0}"
    header = {"accept": "application/json", "Accept-Language": "hi_IN", \
              "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/90.0.4430.93 Safari/537.36"}
    response = requests.get(url.format(state), headers=header)

    d = response.json()["districts"]

    d_districts = dict()

    for dist in d:
        d_districts[dist["district_id"]] = {"district": dist["district_name"], "state_id": state}

    d_districts = dict(
        sorted(
            d_districts.items(),
            key=lambda x: x[0]
        )
    )
    return d_districts

# db = TinyDB("STATES.json")
# table = db.table("states")
#
# data = table.all()
#
# l_dist = list()
#
# for item in data:
#     _id = item["state_id"]
#     dist = get_district_list(state=_id)
#
#     for k, v in dist.items():
#         l_dist.append(
#             {"district_id": k, "state_id": v['state_id'], "district_name": v["district"]}
#         )

# ddb = TinyDB("DIST.json")
# dtable = ddb.table("district")
#
# for item in l_dist:
#     dtable.insert(item)

# print(dtable.search(Query().state_id == 4))