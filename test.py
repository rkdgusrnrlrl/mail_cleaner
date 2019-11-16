from __future__ import print_function

import json
import os.path
import pickle
from datetime import datetime, timedelta
from functools import reduce

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

before_3day = datetime.now() - timedelta(days=3)
before_1day = datetime.now() - timedelta(days=1)
str_before_3day_date = before_3day.strftime('%Y/%m/%d')
str_before_1day_date = before_1day.strftime('%Y/%m/%d')


def make_query(qq):
    def generate_q(q, kk):
        return q + '%s:%s ' % (kk[0], kk[1])

    keys = qq.items()
    return reduce(generate_q, keys, '')


def handler(event, contaxt):
    credential_file_path = contaxt['token_path']
    delete_query_list2 = contaxt['filter']

    if not os.path.exists(credential_file_path):
        creds = create_credential()
        save_credeential(credential_file_path, creds)
    else:
        creds = load_credential(credential_file_path)

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    rr = service.users().getProfile(userId='me').execute()
    email = rr.get('emailAddress', '')
    print(email)

    for qq in delete_query_list2:
        qq = make_query(qq)
        print(qq)

        rr = service.users().threads().list(userId='me', q=qq).execute()
        threads = rr.get('threads', [])
        delete_thread(service, threads)

        while 'nextPageToken' in rr:
            page_token = rr['nextPageToken']
            rr = service.users().threads().list(userId='me', q=qq, pageToken=page_token).execute()
            threads = rr.get('threads', [])
            delete_thread(service, threads)


def create_credential():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
    return flow.run_console()


def save_credeential(file_path, creds):
    with open(file_path, 'wb') as token:
        pickle.dump(creds, token)
    return creds


def load_credential(file_path):
    if not os.path.exists(file_path):
        print('token file not exist')
        exit(1)

    with open(file_path, 'rb') as token:
        creds = pickle.load(token)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return creds


def delete_thread(service, threads):
    for tt in threads:
        body_read = {'removeLabelIds': ['UNREAD']}
        service.users().threads().modify(userId='me', id=tt['id'], body=body_read).execute()
        thread = service.users().threads().trash(userId='me', id=tt['id']).execute()
        print(thread)


if __name__ == '__main__':
    dd = open('args.json').read()
    dd = json.loads(dd)
    handler(None, dd)
