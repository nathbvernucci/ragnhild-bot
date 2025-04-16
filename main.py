import os
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import random
from http.server import SimpleHTTPRequestHandler, HTTPServer
import asyncio

# Dicionário temporário para armazenar status dos jogadores
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
    await query.edit_message_text(text=f"Você entrou na {choice.upper().replace('_', ' ')}.")

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
            f"MÁFIA: {info['mafia'].upper().replace('_', ' ')}\n"
            f"VIDA: {info['vida']}\n"
            f"FORÇA: {info['força']}"
        )
    else:
        resposta = "Você ainda não escolheu uma máfia. Use /start para começar."
    await update.message.reply_text(resposta)

# Função para rodar o servidor HTTP simples
def run_http_server():
    server = HTTPServer(('0.0.0.0', 8080), SimpleHTTPRequestHandler)
    print("Servidor HTTP iniciado na porta 8080")
    server.serve_forever()

# Função para rodar o bot
async def run_bot():
    from dotenv import load_dotenv
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler("rolar", rolar))
    app.add_handler(CommandHandler("status", status))
    
    await app.run_polling()

# Função principal para rodar o servidor e bot ao mesmo tempo
def main():
    # Rodando o servidor HTTP em uma thread separada
    threading.Thread(target=run_http_server, daemon=True).start()

    # Rodando o bot de forma assíncrona
    asyncio.run(run_bot())

if __name__ == '__main__':
    main()