from cowin_api import CoWinAPI
import requests
from datetime import date
import vaccine_centers
import json

today = date.today().strftime("%d-%m-%Y")
cowin = CoWinAPI()
states = cowin.get_states()['states']

districts = []
for state in states:
    districts.extend(cowin.get_districts(state['state_id'])['districts'])

pins_districts = {}
district_name_id = {}
user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51'}

responses_district_centers = {}
with requests.session() as session:
    session.headers.update(user_agent)
    for district in districts:
        id = district['district_id']
        try:
            response = session.get(f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={id}&date={today}")
            if response.status_code == requests.codes.ok:
                response_centers = vaccine_centers.vaccine_centers_from_dict(json.loads(response.text)).centers
                if id in responses_district_centers.keys():
                    responses_district_centers[id] = responses_district_centers[id].extend(response_centers)
                else:
                    responses_district_centers[id] = response_centers
            else:
                print(f"Error code {response.status_code}")
        except:
            print("Exception")
            print(id)
            continue

    for district_id, centers in responses_district_centers.items():
        pins = set()
        for center in centers:
            pins.add(center.pincode)
        pins = list(pins)
        for pin in pins:
            if pin in pins_districts.keys():
                pins_districts[pin] = pins_districts[pin].extend(district_id)
            else:
                pins_districts[pin] = [district_id]

    print(pins_districts)