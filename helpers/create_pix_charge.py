import requests
import os
import uuid  # Para gerar a chave X-Idempotency-Key
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()

ACCESS_TOKEN = os.getenv("MERCADO_PAGO_ACCESS_TOKEN")

def create_pix_charge(value, description, client_email):
    """
    Gera uma cobrança Pix usando a API do Mercado Pago.
    :param value: Valor da cobrança (float)
    :param description: Descrição da cobrança (str)
    :param client_email: E-mail do cliente (str)
    :return: Dados da cobrança (dict)
    """
    url = "https://api.mercadopago.com/v1/payments"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "X-Idempotency-Key": str(uuid.uuid4())  # Gera um UUID único
    }
    data = {
        "transaction_amount": value,
        "description": description,
        "payment_method_id": "pix",
        "payer": {"email": client_email},
    }
    print(f"Headers enviados: {headers}")
    print(f"Dados enviados para a API: {data}")
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 201:
        print("Cobrança Pix criada com sucesso!")
        return response.json()
    else:
        print("Erro ao gerar cobrança:", response.status_code, response.json())
        return None
