import requests
import json
import vaccine_centers
from datetime import date

rows = {}
responses = {}
filtered_responses = {}
today = date.today().strftime("%d-%m-%Y")


def vaccine_status_pins(pins):
    responses = []
    with requests.session() as session:
        for pin in pins:
            resp = session.get(
                f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={pin}&date={today}")
            responses.extend(vaccine_centers.vaccine_centers_from_dict(json.loads(resp.text)).centers)
    return responses

def parse_email_pins(filename):
    file = open(filename, 'r').readlines()
    for row in file:
        row = row.strip()
        email = str(row.split(';')[0])
        pins = row.split(';')[1].split(',')

        if email in rows.keys():
            currentPINs = rows[email]
            pins.extend(currentPINs)
        rows[email] = list(set(pins))

def generate_center_html(name, pincode, total_capacity, min_age_cumulative, fee_type, vaccine):
    t = f"""
    <tr style="height: 17px;">
<td style="width: 30%; height: 17px;">{name};</td>
<td style="width: 10%; height: 17px;">{pincode};</td>
<td style="width: 20%; height: 17px;">{total_capacity};</td>
<td style="width: 20%; height: 17px;">{min_age_cumulative};</td>
<td style="width: 20%; height: 17px;">{fee_type};</td>
<td style="width: 10%; height: 17px;">{vaccine};</td>
</tr>
    """


if __name__ == '__main__':
    parse_email_pins('emailandPINs')
    for email, pins in rows.items():
        r = vaccine_status_pins(pins)
        responses[email] = r
    for email, centers in responses.items():
        filtered_centers = []
        for center in centers:
            if center.total_capacity > 0:
                filtered_centers.append(center)
        filtered_centers.sort(key=lambda x: x.total_capacity, reverse=True)
        filtered_responses[email] = filtered_centers


    print(responses)
