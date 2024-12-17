import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Importar funções dos helpers
from helpers.create_pix_charge import create_pix_charge
from helpers.fetch_emails import fetch_emails
from helpers.summarize_email import summarize_email
from helpers.verify_payment import verify_payment
from helpers.fetch_emails import authenticate_user
from helpers.fetch_emails import generate_auth_url, authenticate_user

# Carregar variáveis de ambiente
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bem-vindo ao Newsmash!\n"
        "Use /pix para pagar e liberar o serviço.\n"
        "Use /auth para autorizar o acesso ao seu Gmail.\n"
        "Use /summarize para receber o resumo das newsletters."
    )

# Comando /pix
async def pix_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    value = 10.0  # Valor da cobrança em reais
    description = "Acesso ao serviço Newsmash"
    client_email = "cliente@example.com"  # Aqui, substitua pelo email real do cliente

    charge = create_pix_charge(value, description, client_email)
    if charge:
        qr_code = charge["point_of_interaction"]["transaction_data"]["qr_code"]
        await update.message.reply_text(f"Use o QR Code abaixo para pagamento:\n{qr_code}")
    else:
        await update.message.reply_text("Erro ao gerar a cobrança. Tente novamente.")

# Comando /auth
async def auth_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    auth_url = generate_auth_url()
    await update.message.reply_text(
        "Clique no link abaixo para autorizar o acesso ao seu Gmail:\n"
        f"{auth_url}\n\n"
        "Após autorizar, copie o código de autenticação exibido e envie-o aqui no chat no formato: /authcode SEU_CODIGO."
    )

# Comando /authcode
async def authcode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text(
            "Por favor, envie o código de autenticação assim: /authcode SEU_CODIGO."
        )
        return

    auth_code = context.args[0]
    try:
        # Chama a função para autenticar e salvar o token
        authenticate_user(auth_code)
        await update.message.reply_text(
            "Autenticação concluída com sucesso! Use /summarize para ver seus resumos."
        )
    except Exception as e:
        await update.message.reply_text(f"Erro ao autenticar: {str(e)}")


# Comando /summarize
async def summarize_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Buscando emails e gerando resumos. Aguarde...")

    # Passo 1: Buscar emails do cliente
    emails = fetch_emails()

    if not emails:
        await update.message.reply_text("Nenhum email encontrado ou algo deu errado.")
        return

    # Passo 2: Resumir emails
    summaries = [summarize_email(email) for email in emails]

    # Passo 3: Enviar resumos ao cliente
    for summary in summaries:
        await update.message.reply_text(summary)

# Configuração do bot
def main():
    print("Iniciando o bot...")

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Adicione os comandos ao bot
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("pix", pix_command))
    application.add_handler(CommandHandler("auth", auth_command))
    application.add_handler(CommandHandler("authcode", authcode_command))
    application.add_handler(CommandHandler("summarize", summarize_command))

    # Inicie o bot
    print("Bot está rodando...")
    application.run_polling()

if __name__ == "__main__":
    main()
