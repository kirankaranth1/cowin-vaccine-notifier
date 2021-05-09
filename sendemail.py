from Google import Create_Service
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

accounts = ['vaccinenotificationcowin2', 'vaccinenotifier1', 'vaccinenotificationcowin3', 'vaccinenotificationcowin4']

lastused_file = 'lastusedemail.txt'
file = open(lastused_file, 'r')

last_used_account = file.read().strip()
last_used_index = accounts.index(last_used_account)

if last_used_index == len(accounts) - 1:
    current_index = 0
else:
    current_index = last_used_index + 1

file.close()
ACCOUNT = accounts[current_index]
print(f"{ACCOUNT} will be used to send email.")
file = open(lastused_file, 'w')
file.write(ACCOUNT)
file.close()

CLIENT_SECRET_FILE = f'emailcreds/{ACCOUNT}.json'
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://mail.google.com/']


service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES, account = ACCOUNT)

def send_gmail(html, to, subject):
    emailMsg = html
    mimeMessage = MIMEMultipart()
    mimeMessage['to'] = to
    mimeMessage['subject'] = subject
    mimeMessage.attach(MIMEText(emailMsg, 'html'))
    raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()

    message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()
    print(message)