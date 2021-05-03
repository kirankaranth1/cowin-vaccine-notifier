import os
import hashlib
import requests
import json

import sendemail
import vaccine_centers
from datetime import date

rows = {}
responses = {}
filtered_responses_html = {}
filtered_responses_signature = {}
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
        rows[email] = sorted(list(set(pins)))


def generate_center_html(name, pincode, total_capacity, min_age_cumulative, fee_type, vaccine):
    return f"""
    <tr style="height: 17px;">
<td style="width: 30%; height: 17px;">{name}</td>
<td style="width: 10%; height: 17px;">{pincode}</td>
<td style="width: 20%; height: 17px;">{total_capacity}</td>
<td style="width: 20%; height: 17px;">{min_age_cumulative}</td>
<td style="width: 20%; height: 17px;">{fee_type}</td>
<td style="width: 10%; height: 17px;">{vaccine}</td>
</tr>
    """


def generate_filtered_centers_table(centers, pins):
    header = f""" <p>Hi,</p> <p>This email contains latest availability of vaccines for your PIN codes. All data is 
    retrieved from Cowin. Additional notifications will be sent if there are changes to the current status below.</p> 
    <p>The following PIN codes were checked: {pins}</p> 
    <table style="border-collapse: collapse; width: 100%; height: 69px;" border="1">
<tbody>
<tr style="height: 52px;">
<td style="width: 30%; height: 52px;"><strong>Center</strong></td>
<td style="width: 10%; height: 52px;"><strong>Pin code</strong></td>
<td style="width: 20%; height: 52px;"><strong>Number of slots available this week</strong></td>
<td style="width: 20%; height: 52px;"><strong>Minimum age limit</strong></td>
<td style="width: 20%; height: 52px;"><strong>Fee type</strong></td>
<td style="width: 10%; height: 52px;"><strong>Vaccine name</strong></td>
</tr>"""

    footer = """
    </tbody>
</table>"""

    table = ""

    for center in centers:
        table += generate_center_html(center.name, center.pincode, center.total_capacity, center.min_age_cumulative,
                                      center.fee_type, center.vaccine)

    return header + table + footer


def generate_filtered_centers_signature(centers, pins):
    sig = ''
    centers.sort(key= lambda x: x.center_id)
    for c in centers:
        sig += str(c.center_id)
    sig += pins
    print(f"Signature: {sig}")
    return hashlib.sha1(sig.encode("UTF-8")).hexdigest()[:5]

def check_write_signature_match(email, signature):
    sig_hash = hashlib.sha1(email.encode("UTF-8")).hexdigest()[:10] + "." + signature
    if not os.path.isdir("sig"):
        os.makedirs("sig")
        open(f'sig/{sig_hash}', 'a').close()
        return False
    else:
        if os.path.isfile(f'sig/{sig_hash}'):
            return True;
        else:
            open(f'sig/{sig_hash}', 'a').close()
            return False


if __name__ == '__main__':
    parse_email_pins('emailandPINs')
    for email, pins in rows.items():
        r = vaccine_status_pins(pins)
        responses[(email, ','.join(pins))] = r
    for (email, pins), centers in responses.items():
        filtered_centers = []
        for center in centers:
            if center.total_capacity > 0:
                filtered_centers.append(center)
        filtered_centers.sort(key=lambda x: x.total_capacity, reverse=True)
        filtered_responses_html[email] = generate_filtered_centers_table(filtered_centers, pins)
        filtered_responses_signature[email] = generate_filtered_centers_signature(filtered_centers, pins)

    for email, signature in filtered_responses_signature.items():
        if check_write_signature_match(email, signature):
            print("Signature match. Not sending email.")
        else:
            sendemail.send_gmail(filtered_responses_html[email], email, "Latest vaccine availability report")

    print(filtered_responses_html)
