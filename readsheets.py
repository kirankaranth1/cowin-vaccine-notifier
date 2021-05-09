import os
from Google import Create_Service

CLIENT_SECRET_FILE = 'client_secret_new.json'
API_SERVICE_NAME = 'sheets'
API_VERSION = 'v4'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

service = Create_Service(CLIENT_SECRET_FILE, API_SERVICE_NAME, API_VERSION, SCOPES)

sheet_id = '1qZJtt35YHiz-pZZY72VogMbmdjEn3VWEjmrlBCHzUVM'
unsub_id = '1zoq-nVzmycjOUEBO5W8prhSNr02AmuAPA3YEyTDE_OY'

values = service.spreadsheets().values()
result = values.get(spreadsheetId=sheet_id, range='B2:D').execute()
rows = result.get('values', [])

unsub_list = values.get(spreadsheetId=unsub_id, range='B2:D').execute()
unsub_list_rows = unsub_list.get('values', [])

def get_email_pins_dict():
    dict = {}

    for row in rows:
        email = row[0].strip()
        pins = row[1].split(';')

        if email in dict.keys():
            currentPINs = dict[email]
            pins.extend(currentPINs)
        dict[email] = sorted(list(set(pins)))
    return dict

def get_unsub_list_set():
    s = set()

    for unsub_list_row in unsub_list_rows:
        s.add(unsub_list_row[0])
    return s