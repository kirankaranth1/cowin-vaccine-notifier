import os
from Google import Create_Service

CLIENT_SECRET_FILE = 'cowinnotifier-828dd5102df9.json'
API_SERVICE_NAME = 'sheets'
API_VERSION = 'v4'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

service = Create_Service(CLIENT_SECRET_FILE, API_SERVICE_NAME, API_VERSION, SCOPES)

sheet_id = '1qZJtt35YHiz-pZZY72VogMbmdjEn3VWEjmrlBCHzUVM'

values = service.spreadsheets().values()
result = values.get(spreadsheetId=sheet_id, range='B2:D').execute()
rows = result.get('values', [])

def get_email_pins_dict():
    dict = {}
    for row in rows:
        dict[row[0]] = row[1]
    return dict