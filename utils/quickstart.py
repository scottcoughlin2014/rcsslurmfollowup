from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import os
import base64

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.encoders import encode_base64
import mimetypes
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send',]
#          'https://www.googleapis.com/auth/drive.file']

def get_credentials(credentials_json=None, credentials_token=None):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    if (credentials_json is None) and (credentials_token is None):
        raise ValueError("Need to either supply a path to the creditals.json "
                         "or to the token.pickle file")
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if (credentials_token is not None) and (os.path.exists(credentials_token)):
        with open(credentials_token, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_json, SCOPES)
            creds = flow.run_console()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def create_message(to, message_text, subject, sender="scottcoughlin2014@u.northwestern.edu",
                   text_type='plain'):
    """Create a message for an email.

    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

    Returns:
    An object containing a base64url encoded email object.
    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text, text_type)
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_string().encode('UTF-8')).decode('ascii')}

def send_message(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    print('Message Id: %s' % message['id'])
    return message
  except errors.HttpError:
    print('An error occurred: %s' % error)

def send_followup(message_text, to, subject, text_type='plain', **kwargs):
    creds = get_credentials(**kwargs)
    service = build('gmail', 'v1', credentials=creds)
    message = create_message(to=to, message_text=message_text, text_type=text_type, subject=subject)
    send_message(service, 'me', message)
    return True
