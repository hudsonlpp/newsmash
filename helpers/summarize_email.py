import os
from dotenv import load_dotenv
import openai

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

print(f"API Key carregada: {openai.api_key}")  # Linha de debug

def summarize_email(email_content):
    """Usa a API da OpenAI para resumir o conteúdo do email."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente que resume emails de forma breve."},
                {"role": "user", "content": f"Resuma o seguinte email:\n\n{email_content}"}
            ],
            temperature=0.5,
            max_tokens=100
        )
        summary = response['choices'][0]['message']['content'].strip()
        return summary
    except Exception as e:
        print(f"Erro ao gerar resumo: {e}")
        return "Erro ao gerar resumo do email."
