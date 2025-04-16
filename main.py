import logging
import os
import random
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Setup de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dicionários globais
mafia_nomes = {
    "outfit": "Outfit",
    "camorra": "Camorra",
    "famiglia": "Famiglia"
}

pontos_mafias = {
    "Outfit": {"vida": 0, "forca": 0},
    "Camorra": {"vida": 0, "forca": 0},
    "Famiglia": {"vida": 0, "forca": 0},
}

jogadores = {}

# Ações especiais por habilidade
habilidades_especiais = ["furtividade", "blefe", "suborno"]

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Outfit", callback_data="escolha_outfit")],
        [InlineKeyboardButton("Camorra", callback_data="escolha_camorra")],
        [InlineKeyboardButton("Famiglia", callback_data="escolha_famiglia")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Escolha sua máfia:", reply_markup=reply_markup)

# Callback de escolha de máfia
async def escolha_mafia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    escolha = query.data.split("_")[1]
    user = query.from_user

    maf = mafia_nomes.get(escolha, "Outfit")
    jogadores[user.id] = {
        "nome": user.first_name,
        "mafia": maf,
        "vida": random.randint(70, 100),
        "forca": random.randint(30, 70),
        "agilidade": random.randint(20, 50),
        "habilidade": random.choice(habilidades_especiais)
    }

    await query.edit_message_text(text=f"Você entrou na máfia *{maf}*!",
                                  parse_mode="Markdown")

# Comando /status
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_text = "Pontuação atual por máfia:\n\n"
    for nome, pontos in pontos_mafias.items():
        status_text += f"*{nome}* - Vida: {pontos['vida']}, Força: {pontos['forca']}\n"
    await update.message.reply_text(status_text, parse_mode="Markdown")

# Comando /rolar
async def rolar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if user.id not in jogadores:
        await update.message.reply_text("Você precisa escolher uma máfia primeiro com /start.")
        return

    resultado = random.randint(1, 20)
    await update.message.reply_text(f"{user.first_name} rolou um dado e tirou: *{resultado}*",
                                    parse_mode="Markdown")

# Comando /ficha
async def ficha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if user.id not in jogadores:
        await update.message.reply_text("Você ainda não criou sua ficha. Use /start.")
        return

    f = jogadores[user.id]
    texto = (
        f"Ficha de *{f['nome']}*\n"
        f"Máfia: *{f['mafia']}*\n"
        f"Vida: {f['vida']}\n"
        f"Força: {f['forca']}\n"
        f"Agilidade: {f['agilidade']}\n"
        f"Habilidade Especial: *{f['habilidade']}*"
    )
    await update.message.reply_text(texto, parse_mode="Markdown")

# Inicialização do bot
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("rolar", rolar))
    app.add_handler(CommandHandler("ficha", ficha))
    app.add_handler(CallbackQueryHandler(escolha_mafia, pattern="^escolha_"))

    logger.info("Bot está rodando...")
    app.run_polling()

if __name__ == "__main__":
    main()