import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_email(email_content):
    """Resume o conteúdo do email usando OpenAI."""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é um assistente que resume emails de forma clara e objetiva."},
            {"role": "user", "content": email_content},
        ]
    )
    return response['choices'][0]['message']['content']
