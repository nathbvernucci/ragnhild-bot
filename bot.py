import os
import random
import asyncio
import logging
from http.server import HTTPServer, SimpleHTTPRequestHandler
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)

# === Configuração de Logging ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# === Banco de Dados Temporário ===
jogadores = {}
pontuacoes = {"Outfit": 0, "Camorra": 0, "Famiglia": 0}
cargos = ["Infiltrador", "Atirador", "Negociador", "Líder Tático"]

# === Comandos do Jogo ===

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("Entrar na Outfit", callback_data='Outfit'),
        InlineKeyboardButton("Entrar na Camorra", callback_data='Camorra'),
        InlineKeyboardButton("Entrar na Famiglia", callback_data='Famiglia')
    ]]
    await update.message.reply_text(
        "Bem-vindo à *Operação Ragnhild*!\n\nO ar está denso e as sombras se estendem. A guerra entre as máfias está prestes a começar."
        "\n\nEscolha sua máfia e prepare-se para fazer sua marca nesse jogo de poder e traição.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# Callback de escolha de máfia
async def escolher_mafia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    escolha = query.data
    jogadores[user_id] = {
        "mafia": escolha,
        "vida": 100,
        "força": random.randint(5, 20),
        "cargo": None
    }
    await query.edit_message_text(f"Você escolheu a {escolha.upper()}! Prepare-se para a guerra.")

# /rolar
async def rolar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        arg = context.args[0]
        qtd, faces = map(int, arg.lower().split('d'))
        resultados = [random.randint(1, faces) for _ in range(qtd)]
        total = sum(resultados)
        await update.message.reply_text(f"Você rolou: {resultados} | Total: {total}")
    except Exception:
        await update.message.reply_text("Use o formato: /rolar 1d20")

# /status
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    jogador = jogadores.get(user_id)
    if jogador:
        await update.message.reply_text(
            f"Máfia: {jogador['mafia'].upper()}\n"
            f"Vida: {jogador['vida']}\n"
            f"Força: {jogador['força']}\n"
            f"Cargo: {jogador['cargo'] or 'Nenhum'}"
        )
    else:
        await update.message.reply_text("Use /start para escolher sua máfia.")

# /cargo
async def cargo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in jogadores:
        await update.message.reply_text("Escolha sua máfia primeiro com /start.")
        return
    if jogadores[user_id]['cargo']:
        await update.message.reply_text(f"Você já escolheu: {jogadores[user_id]['cargo']}")
        return
    keyboard = [[InlineKeyboardButton(c, callback_data=c)] for c in cargos]
    await update.message.reply_text("Escolha seu cargo:", reply_markup=InlineKeyboardMarkup(keyboard))

# Callback para definir cargo
async def definir_cargo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cargo = query.data
    user_id = query.from_user.id
    if user_id in jogadores:
        jogadores[user_id]['cargo'] = cargo
        await query.edit_message_text(f"Cargo definido: {cargo}")
    else:
        await query.edit_message_text("Escolha uma máfia primeiro com /start.")

# /sala_vip
async def sala_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in jogadores:
        await update.message.reply_text("Escolha sua máfia primeiro com /start.")
        return
    texto = "Você quer tentar acessar a Sala VIP?"
    keyboard = [[InlineKeyboardButton("Entrar na Sala VIP", callback_data='entrar_vip')]]
    await update.message.reply_text(texto, reply_markup=InlineKeyboardMarkup(keyboard))

# Callback sala VIP
async def entrar_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    jogador = jogadores[user_id]
    resultado = random.randint(1, 20) + jogador['força']
    mafia = jogador['mafia']
    if resultado > 15:
        pontos = random.randint(5, 15)
        pontuacoes[mafia] += pontos
        await query.edit_message_text(f"Sucesso! A {mafia.upper()} ganhou {pontos} pontos.")
    else:
        jogador['vida'] -= 10
        pontuacoes[mafia] -= 5
        await query.edit_message_text(f"Falhou! -10 de vida. {mafia.upper()} perdeu 5 pontos.")

# /cofre
async def cofre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in jogadores:
        await update.message.reply_text("Escolha sua máfia primeiro com /start.")
        return
    keyboard = [[InlineKeyboardButton("Abrir Cofre", callback_data='abrir_cofre')]]
    await update.message.reply_text("Você está diante do cofre. Deseja tentar abrir?", reply_markup=InlineKeyboardMarkup(keyboard))

# Callback abrir cofre
async def abrir_cofre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    jogador = jogadores[user_id]
    resultado = random.randint(1, 20) + jogador['força']
    mafia = jogador['mafia']
    if resultado > 15:
        loot = random.randint(10, 50)
        pontuacoes[mafia] += loot
        await query.edit_message_text(f"Cofre aberto! {loot} pontos para a {mafia.upper()}.")
    else:
        jogador['vida'] -= 15
        pontuacoes[mafia] -= 10
        await query.edit_message_text(f"Falha! -15 de vida. {mafia.upper()} perdeu 10 pontos.")

# /pontuacao
async def pontuacao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resultado = "\n".join([f"{mafia}: {pontos}" for mafia, pontos in pontuacoes.items()])
    await update.message.reply_text(f"Pontuação atual:\n{resultado}")

# /final
async def final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    jogador = jogadores.get(user_id)
    if not jogador:
        await update.message.reply_text("Use /start para entrar no jogo.")
        return

    pontos = pontuacoes[jogador['mafia']]
    if pontos >= 70:
        final = "Vitória Suprema: fuga de helicóptero, Palácio em chamas."
    elif 40 <= pontos < 70:
        final = "Final Intermediário: perdas e glória parcial."
    else:
        final = "Final Trágico: você foge ferido entre sirenes e caos."

    await update.message.reply_text(f"Final da {jogador['mafia'].upper()}:\n{final}")

# === Funções de Execução ===

# Rodar servidor web básico para manter Render ativo
def run_web_server():
    server = HTTPServer(("0.0.0.0", 8080), SimpleHTTPRequestHandler)
    server.serve_forever()

# Inicializa o bot
async def main():
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN não encontrado no .env")

    app = ApplicationBuilder().token(token).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(escolher_mafia, pattern='^(Outfit|Camorra|Famiglia)$'))
    app.add_handler(CommandHandler("rolar", rolar))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("cargo", cargo))
    app.add_handler(CallbackQueryHandler(definir_cargo, pattern='^(Infiltrador|Atirador|Negociador|Líder Tático)$'))
    app.add_handler(CommandHandler("sala_vip", sala_vip))
    app.add_handler(CallbackQueryHandler(entrar_vip, pattern='entrar_vip'))
    app.add_handler(CommandHandler("cofre", cofre))
    app.add_handler(CallbackQueryHandler(abrir_cofre, pattern='abrir_cofre'))
    app.add_handler(CommandHandler("pontuacao", pontuacao))
    app.add_handler(CommandHandler("final", final))

    await app.run_polling()

# === Execução Final ===
if __name__ == "__main__":
    import threading
    threading.Thread(target=run_web_server, daemon=True).start()
    asyncio.run(main())