from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_user():
    """Autentica o cliente usando OAuth."""
    creds = None
    if creds is None or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def fetch_emails():
    """Busca emails não lidos da caixa de entrada."""
    creds = authenticate_user()
    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(userId='me', q="is:unread").execute()
    messages = results.get('messages', [])
    emails = []
    for msg in messages:
        email = service.users().messages().get(userId='me', id=msg['id']).execute()
        emails.append(email['snippet'])
    return emails
