import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Dados dos jogadores e pontuação por máfia
jogadores = {}
pontuacao_mafias = {"Outfit": 0, "Camorra": 0, "Famiglia": 0}

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Entrar na Outfit", callback_data='Outfit'),
            InlineKeyboardButton("Entrar na Camorra", callback_data='Camorra'),
            InlineKeyboardButton("Entrar na Famiglia", callback_data='Famiglia')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Bem-vindo à Operação Ragnhild! Escolha sua máfia:", reply_markup=reply_markup)

# Escolha da máfia
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    escolha = query.data
    jogadores[user_id] = {"mafia": escolha, "vida": 100, "força": random.randint(5, 20)}
    await query.edit_message_text(f"Você entrou na {escolha}.")

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
            f"MÁFIA: {info['mafia']}\n"
            f"VIDA: {info['vida']}\n"
            f"FORÇA: {info['força']}"
        )
    else:
        resposta = "Você ainda não escolheu uma máfia. Use /start para começar."
    await update.message.reply_text(resposta)

# Comando /sala_vip
async def sala_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Aproximar-se do embaixador", callback_data="vip_aproximar"),
            InlineKeyboardButton("Neutralizar seguranças", callback_data="vip_neutralizar")
        ],
        [InlineKeyboardButton("Explorar a sala", callback_data="vip_explorar")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Você está na Sala VIP. A tensão é alta. O que deseja fazer?", reply_markup=reply_markup
    )

# Comando /cofre
async def cofre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Hackear o painel", callback_data="cofre_hackear"),
            InlineKeyboardButton("Explodir a porta", callback_data="cofre_explodir")
        ],
        [InlineKeyboardButton("Disfarçar-se de segurança", callback_data="cofre_disfarce")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Você está diante do cofre central. O tempo é curto. Qual a sua ação?", reply_markup=reply_markup
    )

# Comando /pontuacao
async def pontuacao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = "\n".join([f"{m}: {p}" for m, p in pontuacao_mafias.items()])
    await update.message.reply_text(f"PONTUAÇÃO DAS MÁFIAS:\n{texto}")

# Comando /ficha
async def ficha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Envie sua ficha no formato:\n\n"
        "Nome: Fulano\n"
        "Idade: 30\n"
        "Cargo na máfia: Executor\n"
        "Habilidade especial: Perícia em explosivos"
    )

# Receber ficha personalizada
async def receber_ficha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    if all(campo in texto for campo in ["Nome:", "Idade:", "Cargo", "Habilidade"]):
        await update.message.reply_text("Ficha registrada com sucesso!")
    else:
        await update.message.reply_text("Formato incorreto. Tente novamente com todos os campos.")

# Respostas de botões da Sala VIP e Cofre
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    respostas = {
        "vip_aproximar": "Você se aproxima do embaixador com discrição...",
        "vip_neutralizar": "Você age rapidamente para desarmar os seguranças...",
        "vip_explorar": "Você observa obras de arte e escutas escondidas...",
        "cofre_hackear": "Você conecta o dispositivo ao painel do cofre...",
        "cofre_explodir": "Você arma os explosivos no ponto exato...",
        "cofre_disfarce": "Você veste o uniforme e caminha como se fosse da segurança..."
    }

    pontuacao = {
        "vip_aproximar": 10,
        "vip_neutralizar": 15,
        "vip_explorar": 5,
        "cofre_hackear": 20,
        "cofre_explodir": 15,
        "cofre_disfarce": 10
    }

    escolha = query.data
    resposta = respostas.get(escolha, "Ação desconhecida.")
    pontos = pontuacao.get(escolha, 0)

    if user_id in jogadores:
        mafia = jogadores[user_id]["mafia"]
        pontuacao_mafias[mafia] += pontos

    await query.edit_message_text(f"{resposta}\n\n(+{pontos} pontos para sua máfia!)")

# Inicializar o bot
async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button, pattern="^(Outfit|Camorra|Famiglia)$"))
    app.add_handler(CallbackQueryHandler(callback))
    app.add_handler(CommandHandler("rolar", rolar))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("sala_vip", sala_vip))
    app.add_handler(CommandHandler("cofre", cofre))
    app.add_handler(CommandHandler("pontuacao", pontuacao))
    app.add_handler(CommandHandler("ficha", ficha))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receber_ficha))

    print("Bot iniciado. Aguardando comandos...")
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())