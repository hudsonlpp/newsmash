import requests
import os

ACCESS_TOKEN = os.getenv("MERCADO_PAGO_ACCESS_TOKEN")

def verify_payment(payment_id):
    """Verifica o status do pagamento usando a API do Mercado Pago."""
    url = f"https://api.mercadopago.com/v1/payments/{payment_id}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("status") == "approved"
    else:
        print("Erro ao verificar pagamento:", response.json())
        return False
