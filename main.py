import os
import hashlib
import time
import requests
import json
import Google
import sendemail
import vaccine_centers
from datetime import date
import readsheets
import uuid
from datetime import datetime
import pytz

rows = {}
responses = {}
response_pin = {}
filtered_responses_html = {}
filtered_responses_signature = {}
today = date.today().strftime("%d-%m-%Y")


def vaccine_status_pins(pins):
    responses = []
    with requests.session() as session:
        session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51'})
        for pin in pins:
            if pin in response_pin.keys():
                responses.extend(response_pin[pin])
            else:
                try:
                    resp = session.get(
                        f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={pin}&date={today}")
                    if resp.status_code == requests.codes.ok:
                        response_centers = vaccine_centers.vaccine_centers_from_dict(json.loads(resp.text)).centers
                        responses.extend(response_centers)
                        response_pin[pin] = response_centers
                    elif resp.status_code == 403:
                        print("Waiting for 5 minutes")
                        time.sleep(300)
                        continue
                except Exception as e:
                    ex = open('exceptions.txt', 'a')
                    print(e)
                    print(pins)
                    print(pin)
                    print(str(e) + '\n' + str(pin) + str(','.join(pins)), file = ex)
                    ex.close()
                    continue
    return responses


def parse_email_pins_file(filename):
    file = open(filename, 'r').readlines()
    for row in file:
        row = row.strip()
        email = str(row.split(';')[0])
        pins = row.split(';')[1].split(',')

        if email in rows.keys():
            currentPINs = rows[email]
            pins.extend(currentPINs)
        rows[email] = sorted(list(set(pins)))

def parse_email_pins_google_sheets():
    email_pins = readsheets.get_email_pins_dict()
    for email, pins in email_pins.items():
        email = email.strip()
        pins_raw = pins.strip().split(';')
        pins = [x for x in pins_raw if x]
        if not len(pins) > 0:
            continue

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
    header = f""" 
    <p>The following PIN codes were checked for vaccine availability: {pins}</p> 
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

    footer = f"""
    </tbody>
</table>
<p>To unsubscribe from these emails go to the below link (Remove spaces)</p>
forms . gle / oY6x4MNryibaPn6y8"""

    table = ""

    if len(centers) > 0:
        for center in centers:
            table += generate_center_html(center.name, center.pincode, center.total_capacity, center.min_age_cumulative,
                                          center.fee_type, center.vaccine)
    else:
        table+="""
          <p><strong>No centers with free slots available for next 7 days</strong></p>
        """

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
    email_sig = hashlib.sha1(email.encode("UTF-8")).hexdigest()[:10]
    sig_hash = email_sig + "." + signature
    if not os.path.isdir("sig"):
        os.makedirs("sig")
        open(f'sig/{sig_hash}', 'a').close()
        return False
    else:
        if os.path.isfile(f'sig/{sig_hash}'):
            return True
        else:
            for file in os.listdir("sig/"):
                if file.startswith(email_sig):
                    print(f"Deleting existing signature for {email}")
                    os.remove(f"sig/{file}")
            open(f'sig/{sig_hash}', 'a').close()
            return False


if __name__ == '__main__':
    parse_email_pins_file('emailandPINs')
    #parse_email_pins_google_sheets()
    unsub_set = readsheets.get_unsub_list_set()
    for email, pins in rows.items():
        if email not in unsub_set:
            r = vaccine_status_pins(pins)
            if len(r) > 0:
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
            print(f"Signature match. Not sending email to {email}.")
        else:
            if email in unsub_set:
                print(f"Not sending email to unsub {email}")
            else:
                print(f"Sending email to {email}")
                now = datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%d-%m-%Y %H:%M:%S")
                sendemail.send_gmail(filtered_responses_html[email], email, f"Vaccine availability report as of {now}")

