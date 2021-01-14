import json
import os.path
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def create_credential():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    return flow.run_console()


def save_credential(creds, file_path):
    with open(file_path, 'wb') as token:
        pickle.dump(creds, token)
    return creds


if __name__ == '__main__':
    dd = open('args.json', encoding='utf-8').read()
    dd = json.loads(dd)
    credential_file_path = dd['token_path']
    if not os.path.exists(credential_file_path):
        creds = create_credential()
        save_credential(creds, credential_file_path)
