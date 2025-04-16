import os
import threading
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import random
from http.server import SimpleHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Dicionário para status dos jogadores
jogadores = {}

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Entrar na Outfit", callback_data='outfit'),
            InlineKeyboardButton("Entrar na Camorra", callback_data='camorra'),
            InlineKeyboardButton("Entrar na Famiglia", callback_data='famiglia'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Bem-vindo à Operação Ragnhild! Escolha sua máfia:", reply_markup=reply_markup)

# Escolha de máfia
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    choice = query.data
    jogadores[user_id] = {"mafia": choice, "vida": 100, "força": random.randint(5, 20)}
    await query.edit_message_text(text=f"Você entrou na {choice.upper()}.")

# Comando /rolar
async def rolar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        arg = context.args[0]
        qtd, dado = map(int, arg.lower().split('d'))
        resultados = [random.randint(1, dado) for _ in range(qtd)]
        total = sum(resultados)
        await update.message.reply_text(f"Resultados: {resultados} | Total: {total}")
    except:
        await update.message.reply_text("Uso correto: /rolar 1d20")

# Comando /status
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in jogadores:
        info = jogadores[user_id]
        resposta = (
            f"MÁFIA: {info['mafia'].upper()}\n"
            f"VIDA: {info['vida']}\n"
            f"FORÇA: {info['força']}"
        )
    else:
        resposta = "Você ainda não escolheu uma máfia. Use /start para começar."
    await update.message.reply_text(resposta)

# Servidor HTTP para manter o Render ativo
def run_http_server():
    server = HTTPServer(('0.0.0.0', 8080), SimpleHTTPRequestHandler)
    print("Servidor HTTP iniciado na porta 8080")
    server.serve_forever()

# Função principal do bot
async def main():
    token = os.getenv("BOT_TOKEN")
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler("rolar", rolar))
    app.add_handler(CommandHandler("status", status))

    print("Bot iniciado. Aguardando comandos...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()

# Início do servidor e execução
if __name__ == "__main__":
    threading.Thread(target=run_http_server, daemon=True).start()

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Caso esteja rodando (Render), usa create_task
            loop.create_task(main())
        else:
            loop.run_until_complete(main())
    except RuntimeError:
        # Caso não exista um loop, cria um novo
        asyncio.run(main())