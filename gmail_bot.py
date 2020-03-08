from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import email
import base64
import pdfkit
​
# If modifying these scopes, delete the file token.pickle.
SCOPES = [
            'https://mail.google.com/',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.settings.basic',
            'https://www.googleapis.com/auth/gmail.metadata'
        ]
def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
​
    service = build('gmail', 'v1', credentials=creds)
​
    filter = {
        'criteria': {
            'from': 'ashik@codemarshal.com'
        },
        'action': {
            'addLabelIds': ['STARRED']
        }
    }
    # results = service.users().settings().filters().create(userId='me', body=filter).execute()
    # print(results)
​
    # getting list of mails having queried criteria
    query = 'from:mehedishafi@hotmail.com subject: uber'
    results = service.users().messages().list(userId='me', q=query).execute()
​
    emails = []
    if results != None:
        for item in results['messages']:
            id_ = item['id']
            emailFull = service.users().messages().get(userId='me', id=id_, format='raw').execute()
            # headers = emailFull["payload"]["headers"]
            # print(emailFull['payload'])
            # subject = [i['value'] for i in headers if i["name"]=="Subject"]
            # emails.append(subject)
            print(emailFull['snippet'])
​
            msg_str = base64.urlsafe_b64decode(emailFull['raw'].encode('ASCII'))
            # print(type(msg_str))
            # # print(msg_str)
            mime = email.message_from_string(msg_str.decode('utf-8'))
​
            print(mime)
​
            return mime
            # # print(msg_str)
​
            # print (mime)
​
            # print(msg_str)
    print(emails)
​
def converToPdf():
    # make html file local as fuck. dump cloud images as base64
    # https://gist.github.com/pansapiens/110431456e8a4ba4f2eb
    # pdfkit 
    pass
​
def parse_html(message):
    '''parse a message and return html_content'''
    content = ''
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == 'text/html':
                content += part.get_payload(None, True).decode('utf-8')
        html_content = content
    else:
        content = message.get_payload(None, True)
        html_content = content.decode('utf-8')
    return html_content
​
if __name__ == '__main__':
    main()
​
# result = gmail_service.users().settings().filters().\
#     create(userId='me', body=filter).execute()