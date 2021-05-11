import hashlib
import os
import requests
import sendemail2
import vaccine_centers
from datetime import date
import time
import json

today = date.today().strftime("%d-%m-%Y")
district_ids = [265, 294, 276]
#district_ids = [97]


def vaccine_slots_district_ids(district_ids):
    '''Gets vaccine slots from cowin with a list of district_ids as input'''
    responses = []
    with requests.session() as session:
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ('
                          'KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 '
                          'Edg/90.0.818.51'})
        for district_id in district_ids:
            try:
                resp = session.get(
                    f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={district_id}&date={today}")
                if resp.status_code == requests.codes.ok:
                    response_centers = vaccine_centers.vaccine_centers_from_dict(json.loads(resp.text)).centers
                    responses.extend(response_centers)
                elif resp.status_code == 403:
                    print("Waiting for 5 minutes")
                    time.sleep(300)
                    continue
            except Exception as e:
                ex = open('exceptions_district.txt', 'a')
                print(e)
                print(district_id)
                print(str(e) + '\n' + str(district_id) + str(','.join(district_id)), file=ex)
                ex.close()
                continue
    return responses


def should_notify(hash_str):
    '''Don't send duplicate notifications when there is no update'''
    if not os.path.isdir("blru45"):
        os.makedirs("blru45")
        open(f'blru45/{hash_str}', 'a').close()
        return True
    else:
        if os.path.isfile(f'blru45/{hash_str}'):
            return False
        else:
            for file in os.listdir("blru45/"):
                os.remove(f"blru45/{file}")
            open(f'blru45/{hash_str}', 'a').close()
            return True


def gen_html(u45dict):
    '''Generates html for dictionary of open slots'''
    header = """<p>Update in 18-44 slots!</p>
    <table style="border-collapse: collapse; width: 100%;" border="1">
    <tbody>
    <tr>
    <td style="width: 25%;"><strong>Centre</strong></td>
    <td style="width: 25%;"><strong>Pincode</strong></td>
    <td style="width: 25%;"><strong>Vaccine name</strong></td>
    <td style="width: 25%;"><strong>Slots left</strong></td>
    </tr>"""
    rows = ""
    for center in u45dict.values():
        rows += f"""<tr>
    <td style="width: 25%;">{center['centre_name']}</td>
    <td style="width: 25%;">{center['pin']}</td>
    <td style="width: 25%;">{center['vaccine']}</td>
    <td style="width: 25%;">{center['capacity']}</td>
    </tr>"""


    footer = """
    </tbody>
    </table>"""

    return header + rows + footer


responses = vaccine_slots_district_ids(district_ids)
u45sessions = {}

for response in responses:
    for session in response.sessions:
        if session.min_age_limit < 46 and session.available_capacity > 0:
            if response.center_id in u45sessions.keys():
                u45sessions[response.center_id]['vaccine'].add(session.vaccine)
                u45sessions[response.center_id]['date'].add(session.date)
                u45sessions[response.center_id]['capacity'] += session.available_capacity
            else:
                u45sessions[response.center_id] = {'centre_name': response.name,
                                                    'pin': response.pincode,
                                                    'vaccine': set([session.vaccine]),
                                                    'capacity': session.available_capacity,
                                                   'date': set([session.date])}

u45sessions_centers_blr = sorted(list((u45sessions.keys())))
u45sessions_centers_blr = [str(c) for c in u45sessions_centers_blr]
u45sessions_centers_blr_str = ''.join(u45sessions_centers_blr)

hash_str = hashlib.sha1(u45sessions_centers_blr_str.encode("UTF-8")).hexdigest()[:10]
html = gen_html(u45sessions)
if should_notify(hash_str):
    sendemail2.send_gmail(html, "vaccinenotifiercowin@gmail.com", "U45 update in Bangalore!!!")
else:
    print("not sending email")


