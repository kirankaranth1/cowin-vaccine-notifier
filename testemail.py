from Google import Create_Service
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

accounts = ['vaccinenotificationcowin2', 'vaccinenotifier1']


ACCOUNT = accounts[1]

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

send_gmail("test", "kirankaranth1@gmail.com", "Test subject")
