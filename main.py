import os
import threading
import random
import asyncio
from http.server import SimpleHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, Application,
    CommandHandler, CallbackQueryHandler,
    ContextTypes
)

# Dicionário temporário para armazenar status dos jogadores
jogadores = {}
pontuacoes = {"Outfit": 0, "Camorra": 0, "Famiglia": 0}

# Cargos possíveis
cargos = [
    "Capo", "Consigliere", "Underboss", "Médico(a)", "Interrogador(a)", 
    "Traficante", "Atirador(a)", "Estrategista", "Hacker", "Executor", "Soldado"
]

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("Entrar na Outfit", callback_data='Outfit'),
        InlineKeyboardButton("Entrar na Camorra", callback_data='Camorra'),
        InlineKeyboardButton("Entrar na Famiglia", callback_data='Famiglia'),
    ]]
    await update.message.reply_text("Bem-vindo à Operação Ragnhild! Escolha sua máfia:",
                                    reply_markup=InlineKeyboardMarkup(keyboard))

# Escolha de máfia
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    choice = query.data
    jogadores[user_id] = {"mafia": choice, "vida": 100, "força": random.randint(5, 20), "cargo": None}
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
            f"FORÇA: {info['força']}\n"
            f"CARGO: {info['cargo'] if info['cargo'] else 'Nenhum'}"
        )
    else:
        resposta = "Você ainda não escolheu uma máfia. Use /start para começar."
    await update.message.reply_text(resposta)

# Comando /cargo
async def cargo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in jogadores:
        await update.message.reply_text("Você precisa escolher uma máfia primeiro usando /start!")
        return
    jogador = jogadores[user_id]
    if jogador['cargo'] is not None:
        await update.message.reply_text(f"Você já escolheu o cargo: {jogador['cargo']}")
        return
    keyboard = [[InlineKeyboardButton(c, callback_data=c)] for c in cargos]
    await update.message.reply_text("Escolha seu cargo:", reply_markup=InlineKeyboardMarkup(keyboard))

async def definir_cargo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    cargo = query.data
    if user_id in jogadores:
        jogadores[user_id]['cargo'] = cargo
        await query.edit_message_text(text=f"Você agora é um {cargo} na máfia {jogadores[user_id]['mafia']}.")
    else:
        await query.edit_message_text(text="Você precisa escolher uma máfia primeiro!")

async def sala_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in jogadores:
        await update.message.reply_text("Você precisa escolher uma máfia antes de acessar a sala VIP!")
        return
    descricao = "Você está na sala VIP. Seu objetivo é reunir informações importantes, mas a segurança está forte. Escolha sabiamente!"
    keyboard = [[InlineKeyboardButton("Tentar acessar a sala VIP", callback_data='entrar_vip')]]
    await update.message.reply_text(descricao, reply_markup=InlineKeyboardMarkup(keyboard))

async def entrar_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if user_id not in jogadores:
        await query.edit_message_text("Você ainda não escolheu uma máfia.")
        return
    jogador = jogadores[user_id]
    resultado = random.randint(1, 20) + jogador['força']
    mafia = jogador['mafia']
    if resultado > 15:
        pontos = random.randint(5, 15)
        pontuacoes[mafia] += pontos
        await query.edit_message_text(f"Sucesso! Você conseguiu acessar a sala VIP e ganhou {pontos} pontos para a {mafia.upper()}.")
    else:
        jogador['vida'] -= 10
        pontuacoes[mafia] -= 5
        await query.edit_message_text(f"Você falhou e perdeu 10 de vida. A {mafia.upper()} perdeu 5 pontos.")

async def cofre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in jogadores:
        await update.message.reply_text("Você precisa escolher uma máfia antes de acessar o cofre!")
        return
    descricao = "Você está na sala do cofre. O objetivo é acessar o cofre e pegar o loot. A segurança está alta. Você precisa da chave certa!"
    keyboard = [[InlineKeyboardButton("Tentar abrir o cofre", callback_data='abrir_cofre')]]
    await update.message.reply_text(descricao, reply_markup=InlineKeyboardMarkup(keyboard))

async def abrir_cofre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if user_id not in jogadores:
        await query.edit_message_text("Você ainda não escolheu uma máfia.")
        return
    jogador = jogadores[user_id]
    resultado = random.randint(1, 20) + jogador['força']
    mafia = jogador['mafia']
    if resultado > 15:
        loot = random.randint(10, 50)
        pontuacoes[mafia] += loot
        await query.edit_message_text(f"Sucesso! Você roubou {loot} pontos! A {mafia.upper()} está mais rica.")
    else:
        jogador['vida'] -= 15
        pontuacoes[mafia] -= 10
        await query.edit_message_text(f"Falha! Você perdeu 15 de vida. A {mafia.upper()} perdeu 10 pontos.")

async def pontuacao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = "\n".join([f"{mafia}: {pontos}" for mafia, pontos in pontuacoes.items()])
    await update.message.reply_text(f"Pontuação atual das máfias:\n{texto}")

# Função para rodar o servidor HTTP
def run_http_server():
    server = HTTPServer(('0.0.0.0', 8080), SimpleHTTPRequestHandler)
    print("Servidor HTTP iniciado na porta 8080")
    server.serve_forever()

# Função principal para iniciar o bot
async def main():
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button, pattern='^(Outfit|Camorra|Famiglia)$'))
    app.add_handler(CommandHandler("rolar", rolar))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("cargo", cargo))
    app.add_handler(CallbackQueryHandler(definir_cargo, pattern='^[A-Za-z ]+$'))
    app.add_handler(CommandHandler("sala_vip", sala_vip))
    app.add_handler(CallbackQueryHandler(entrar_vip, pattern='entrar_vip'))
    app.add_handler(CommandHandler("cofre", cofre))
    app.add_handler(CallbackQueryHandler(abrir_cofre, pattern='abrir_cofre'))
    app.add_handler(CommandHandler("pontuacao", pontuacao))

    await app.initialize()
    await app.start()
    print("Bot rodando!")
    await app.updater.start_polling()
    await app.updater.idle()

# Iniciar servidor HTTP e bot
if __name__ == "__main__":
    threading.Thread(target=run_http_server).start()
    asyncio.run(main())