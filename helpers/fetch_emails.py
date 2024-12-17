from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import pickle
import os

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def generate_auth_url():
    """Gera a URL de autenticação para o cliente."""
    flow = Flow.from_client_secrets_file('credentials.json', SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')
    auth_url, _ = flow.authorization_url(prompt='consent')
    return auth_url

def authenticate_user(auth_code):
    """Completa a autenticação do usuário usando o código fornecido."""
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        SCOPES,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    )
    # Usa o código de autorização para buscar o token
    flow.fetch_token(code=auth_code)
    creds = flow.credentials

    # Salva as credenciais em um arquivo
    with open('token.pickle', 'wb') as token_file:
        pickle.dump(creds, token_file)
    print("Token salvo com sucesso!")

def fetch_emails():
    """Busca emails não lidos da caixa de entrada."""
    creds = None
    
    # Verifica se o token já foi salvo
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token_file:
            creds = pickle.load(token_file)

    # Caso não haja credenciais válidas
    if not creds or not creds.valid:
        raise Exception("Token inválido ou não encontrado. Use /auth para autenticar novamente.")
    
    try:
        # Constrói o serviço da API Gmail
        service = build('gmail', 'v1', credentials=creds)
        
        # Busca mensagens não lidas
        results = service.users().messages().list(userId='me', q="is:unread").execute()
        messages = results.get('messages', [])
        
        # Extrai o snippet (resumo curto) das mensagens
        emails = []
        for msg in messages[:5]:  # Limita a 5 emails para teste
            email = service.users().messages().get(userId='me', id=msg['id']).execute()
            emails.append(email['snippet'])
        
        return emails
    
    except Exception as e:
        print(f"Erro ao buscar emails: {e}")
        return []
