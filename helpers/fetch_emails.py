from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import os
import pickle
import base64
import re
from bs4 import BeautifulSoup

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
    flow.fetch_token(code=auth_code)
    creds = flow.credentials

    with open('token.pickle', 'wb') as token_file:
        pickle.dump(creds, token_file)
    print("Token salvo com sucesso!")

def fetch_emails():
    """Busca emails do rótulo 'Newsletters' e filtra por palavras-chave."""
    creds = None
    
    # Carrega as credenciais
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token_file:
            creds = pickle.load(token_file)
    else:
        raise Exception("Token inválido ou não encontrado. Use /auth para autenticar novamente.")
    
    try:
        # Constrói o serviço do Gmail
        service = build('gmail', 'v1', credentials=creds)

        # Obtém o ID do rótulo "Newsletters"
        label_id = get_label_id(service, 'Newsletters')
        if not label_id:
            print("Etiqueta 'Newsletters' não encontrada.")
            return []

        # Busca emails do rótulo "Newsletters" das últimas 24 horas
        query = "label:Newsletters newer_than:1d"
        results = service.users().messages().list(userId='me', q=query, maxResults=10).execute()
        messages = results.get('messages', [])

        # Processa cada email
        newsletters = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            payload = msg['payload']
            headers = payload.get("headers")
            subject = next((header['value'] for header in headers if header['name'] == 'Subject'), "Sem Assunto")

            # Extrai o corpo do email
            body = extract_body(payload)
            if is_newsletter(body):
                newsletters.append({'subject': subject, 'body': body})

        return newsletters

    except Exception as e:
        print(f"Erro ao buscar emails: {e}")
        return []

def get_label_id(service, label_name):
    """Retorna o ID do rótulo com base no nome."""
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    for label in labels:
        if label['name'] == label_name:
            return label['id']
    return None

def is_newsletter(email_text):
    """Verifica se o email tem características de newsletter usando palavras-chave."""
    newsletter_keywords = [
        'unsubscribe', 
        'newsletter', 
        'boletim informativo', 
        'clique aqui para sair da lista',
        'cancelar inscrição', 
        'gerenciar assinatura', 
        'você está recebendo este email porque',
        'para não receber mais'
    ]
    return any(re.search(keyword, email_text, re.IGNORECASE) for keyword in newsletter_keywords)

def extract_body(payload):
    """Extrai e decodifica o corpo do email."""
    body = ''
    if 'parts' in payload:
        for part in payload['parts']:
            if part.get('mimeType') == 'text/html':
                body = part['body'].get('data')
            elif part.get('mimeType') == 'text/plain':
                body = part['body'].get('data')

    if body:
        body = base64.urlsafe_b64decode(body).decode('utf-8')

    # Limpa HTML e extrai o texto
    soup = BeautifulSoup(body, 'html.parser')
    return soup.get_text(strip=True)
