
from __future__ import print_function

import os.path
import re
patt = re.compile("<(.+)>")

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
EMAILS_PER_REQUEST = "2"
GMAIL_CALLS = "2"
email_file = open("from_emails.txt","a+")

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        next_token= input("Enter token to continue (If not token given, will start from beginning):")
        email_per_request = int(input(f"How many email should be read per request({EMAILS_PER_REQUEST})?") or EMAILS_PER_REQUEST)
        gmail_calls = int(input(f"How many requests should be done({GMAIL_CALLS})?") or GMAIL_CALLS)

        print('Messages:')
        for i in range(gmail_calls):
            result = service.users().messages().list(userId='me',q="is:unread",maxResults=email_per_request,pageToken=next_token).execute()
            messages = result.get('messages')
            next_token = result["nextPageToken"]

            if not messages:
                print('No messages found.')
                return
            for msg in messages:
                txt = service.users().messages().get(userId='me', id=msg['id']).execute()

                try:
                    payload = txt['payload']
                    headers = payload['headers']   
                    for d in headers:
                        if d['name'] == 'From':
                            sender = patt.findall(d['value'])[0]
                    print(f"Id: {msg['id']}, From: {sender}" )  
                    email_file.writelines(f"{sender}\n") 
                except:
                    pass      
        print(f"Last read token: {next_token}")
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')

    email_file.close()

if __name__ == '__main__':
    main()