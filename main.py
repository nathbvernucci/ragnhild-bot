import os
import random
import asyncio
import threading
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Dicionário temporário para armazenar status dos jogadores
jogadores = {}
pontuacoes = {"Outfit": 0, "Camorra": 0, "Famiglia": 0}

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("Entrar na Outfit", callback_data='Outfit'),
        InlineKeyboardButton("Entrar na Camorra", callback_data='Camorra'),
        InlineKeyboardButton("Entrar na Famiglia", callback_data='Famiglia'),
    ]]
    await update.message.reply_text(
        "Bem-vindo à Operação Ragnhild! O ar está denso e as sombras se estendem. A guerra entre as máfias está prestes a começar."
        "\nEscolha sua máfia e prepare-se para fazer sua marca nesse jogo de poder e traição.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Escolha de máfia
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    choice = query.data
    jogadores[user_id] = {"mafia": choice, "vida": 100, "força": random.randint(5, 20), "cargo": None}
    await query.edit_message_text(
        text=f"Você escolheu a {choice.upper()}... A partir de agora, você fará parte dessa família implacável. Prepare-se para tudo."
    )

# Comando /rolar
async def rolar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        arg = context.args[0]
        qtd, dado = map(int, arg.lower().split('d'))
        resultados = [random.randint(1, dado) for _ in range(qtd)]
        total = sum(resultados)
        await update.message.reply_text(f"Você rolou: {resultados} | Total: {total}. A sorte está lançada."
                                        " O destino não perdoa.")
    except:
        await update.message.reply_text("Erro no comando. Use: /rolar 1d20.")

# Comando /status
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in jogadores:
        info = jogadores[user_id]
        resposta = (
            f"Você está na {info['mafia'].upper()}.\n"
            f"VIDA: {info['vida']}\n"
            f"FORÇA: {info['força']}\n"
            f"CARGO: {info['cargo'] if info['cargo'] else 'Nenhum'}"
        )
    else:
        resposta = "Você ainda não escolheu uma máfia. Use /start para se alistar."
    await update.message.reply_text(resposta)

# Comando /cargo
async def cargo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in jogadores:
        await update.message.reply_text("Você ainda não escolheu uma máfia. Use /start para entrar na batalha!")
        return
    jogador = jogadores[user_id]
    if jogador['cargo'] is not None:
        await update.message.reply_text(f"Você já tem um cargo: {jogador['cargo']}. O poder está em suas mãos.")
        return
    keyboard = [[InlineKeyboardButton(c, callback_data=c)] for c in cargos]
    await update.message.reply_text(
        "A guerra é imprevisível. Escolha seu cargo e prepare-se para a batalha decisiva!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def definir_cargo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    cargo = query.data
    if user_id in jogadores:
        jogadores[user_id]['cargo'] = cargo
        await query.edit_message_text(
            text=f"Você agora é um {cargo}. Prepare-se para enfrentar o impossível e ascender ao poder."
        )
    else:
        await query.edit_message_text(text="Você precisa escolher uma máfia antes de receber seu cargo!")

# Sala VIP - Interação cinematográfica
async def sala_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in jogadores:
        await update.message.reply_text("Você precisa escolher uma máfia antes de acessar a sala VIP!")
        return
    descricao = (
        "Você se aproxima da Sala VIP, um lugar sagrado para os poucos que têm permissão. O cheiro de charutos caros e a música baixa"
        " dão uma sensação de poder absoluto. Mas ao entrar, você percebe que as paredes não são tão seguras quanto parecem."
        "\nA segurança aumentou, e você tem uma decisão a fazer. Cada passo seu pode ser o último."
    )
    keyboard = [[InlineKeyboardButton("Tentar entrar na sala VIP", callback_data='entrar_vip')]]
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
        await query.edit_message_text(
            f"Você conseguiu entrar na Sala VIP e desvendou segredos preciosos. A {mafia.upper()} agora possui {pontos} pontos."
        )
    else:
        jogador['vida'] -= 10
        pontuacoes[mafia] -= 5
        await query.edit_message_text(
            f"Falha! A segurança te pegou, e você sofreu 10 de dano. A {mafia.upper()} perdeu 5 pontos."
        )

# Cofre - Interação cinematográfica
async def cofre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in jogadores:
        await update.message.reply_text("Você precisa escolher uma máfia antes de acessar o cofre!")
        return
    descricao = (
        "Você chega à porta do cofre, o som da rotação da fechadura ecoa na sala silenciosa. Uma luz fria ilumina os pesos de ouro"
        " e o dinheiro acumulado, mas não há tempo para admiração. A segurança está em todo lugar, e cada movimento seu é crucial."
        "\nVocê deve escolher com sabedoria como agir."
    )
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
        await query.edit_message_text(
            f"Você abriu o cofre e coletou {loot} pontos! O brilho do ouro agora é seu. A {mafia.upper()} se torna mais forte."
        )
    else:
        jogador['vida'] -= 15
        pontuacoes[mafia] -= 10
        await query.edit_message_text(
            f"Falha! A segurança disparou o alarme. Você perdeu 15 de vida. A {mafia.upper()} perdeu 10 pontos."
        )

# Comando de pontuação
async def pontuacao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = "\n".join([f"{mafia}: {pontos}" for mafia, pontos in pontuacoes.items()])
    await update.message.reply_text(f"Pontuação atual das máfias:\n{texto}")

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
    app.add_handler(CallbackQueryHandler(entrar_vip, pattern='entrar'))