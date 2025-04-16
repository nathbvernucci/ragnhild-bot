import os
import random
from http.server import HTTPServer, SimpleHTTPRequestHandler
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler
)

# Dados dos jogadores e pontuação das máfias
jogadores = {}
pontuacoes = {"Outfit": 0, "Camorra": 0, "Famiglia": 0}

# === Comando /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Outfit", callback_data='Outfit')],
        [InlineKeyboardButton("Camorra", callback_data='Camorra')],
        [InlineKeyboardButton("Famiglia", callback_data='Famiglia')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Escolha sua máfia:", reply_markup=reply_markup)

async def escolher_mafia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    jogadores[user_id] = {"mafia": query.data, "vida": 100, "forca": 50, "carisma": 50, "cargo": None}
    await query.edit_message_text(text=f"Você entrou na máfia: {query.data}")

# === Comando /cargo ===
async def cargo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Infiltrador", callback_data='Infiltrador')],
        [InlineKeyboardButton("Atirador", callback_data='Atirador')],
        [InlineKeyboardButton("Negociador", callback_data='Negociador')],
        [InlineKeyboardButton("Líder Tático", callback_data='Líder Tático')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Escolha seu cargo:", reply_markup=reply_markup)

async def definir_cargo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if user_id in jogadores:
        jogadores[user_id]["cargo"] = query.data
        await query.edit_message_text(text=f"Cargo definido como: {query.data}")
    else:
        await query.edit_message_text(text="Escolha uma máfia primeiro com /start.")

# === Comando /rolar ===
async def rolar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resultado = random.randint(1, 6)
    await update.message.reply_text(f"Você rolou um dado e tirou: {resultado}")

# === Comando /status ===
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    jogador = jogadores.get(user_id)
    if jogador:
        ficha = (
            f"MÁFIA: {jogador['mafia']}\n"
            f"VIDA: {jogador['vida']}\n"
            f"FORÇA: {jogador['forca']}\n"
            f"CARISMA: {jogador['carisma']}\n"
            f"CARGO: {jogador['cargo'] or 'Não definido'}"
        )
        await update.message.reply_text(ficha)
    else:
        await update.message.reply_text("Você ainda não entrou em uma máfia. Use /start.")

# === Comando /sala_vip ===
async def sala_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    jogador = jogadores.get(user_id)
    if not jogador:
        await update.message.reply_text("Você precisa escolher uma máfia primeiro usando /start.")
        return

    texto = (
        "Você adentra a Sala VIP do Palácio Ragnhild. O brilho dos lustres de cristal reflete nos olhos atentos dos seguranças. "
        "O embaixador está cercado por empresários, e você precisa agir com cuidado.\n\n"
        "**Escolha sua ação:**\n"
        "1. Abordar o embaixador diretamente com carisma.\n"
        "2. Distrair os seguranças com uma briga falsa.\n"
        "3. Usar furtividade para plantar um dispositivo de escuta.\n"
        "4. Subornar o garçom para entregar um bilhete ao embaixador."
    )
    await update.message.reply_text(texto)

    # Sistema de pontuação baseado no cargo
    cargo = jogador.get("cargo")
    if cargo == "Negociador":
        pontuacoes[jogador["mafia"]] += 30
        await update.message.reply_text("Seu carisma impressiona o embaixador. +30 pontos para sua máfia.")
    elif cargo == "Infiltrador":
        pontuacoes[jogador["mafia"]] += 20
        await update.message.reply_text("Você planta o dispositivo sem ser visto. +20 pontos para sua máfia.")
    elif cargo == "Atirador":
        pontuacoes[jogador["mafia"]] += 10
        await update.message.reply_text("Você cria uma distração com precisão. +10 pontos para sua máfia.")
    else:
        pontuacoes[jogador["mafia"]] += 5
        await update.message.reply_text("Sua ação foi eficaz, mas discreta. +5 pontos.")

# === Comando /cofre ===
async def cofre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    jogador = jogadores.get(user_id)
    if not jogador:
        await update.message.reply_text("Você precisa escolher uma máfia primeiro usando /start.")
        return

    texto = (
        "Você alcança o cofre subterrâneo do Palácio. As luzes piscam e o tempo está contra você.\n\n"
        "**Ação final:**\n"
        "1. Hackear o sistema com ajuda remota.\n"
        "2. Explodir o cofre com C4.\n"
        "3. Ameaçar o gerente do leilão com uma arma.\n"
        "4. Forjar uma chave mestra baseada nos planos roubados."
    )
    await update.message.reply_text(texto)

    cargo = jogador.get("cargo")
    if cargo == "Líder Tático":
        pontuacoes[jogador["mafia"]] += 30
        await update.message.reply_text("Você coordena a equipe com maestria. +30 pontos.")
    elif cargo == "Infiltrador":
        pontuacoes[jogador["mafia"]] += 20
        await update.message.reply_text("Você encontra a entrada oculta e acessa o cofre. +20 pontos.")
    elif cargo == "Atirador":
        pontuacoes[jogador["mafia"]] += 15
        await update.message.reply_text("Você neutraliza os seguranças com precisão. +15 pontos.")
    else:
        pontuacoes[jogador["mafia"]] += 5
        await update.message.reply_text("Sua presença intimidadora ajuda no assalto. +5 pontos.")

    # Final baseado na pontuação
    pontos = pontuacoes[jogador['mafia']]
    if pontos >= 70:
        final = "Vitória Suprema: sua fuga é impecável, você sai em um carro blindado enquanto o palácio explode ao fundo."
    elif 40 <= pontos < 70:
        final = "Final Intermediário: seu nome será lembrado, mas não sem sacrifícios. A fuga é tumultuada, mas você escapa."
    else:
        final = "Final Trágico: a perseguição é implacável. Você é forçado a fugir pelas ruas escuras, ferido, mas vivo."

    await update.message.reply_text(f"Final da {jogador['mafia'].upper()}:\n{final}")

# === Funções de execução ===
def run_web_server():
    server = HTTPServer(("0.0.0.0", 8080), SimpleHTTPRequestHandler)
    server.serve_forever()

async def main():
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN não encontrado no .env")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(escolher_mafia, pattern='^(Outfit|Camorra|Famiglia)$'))
    app.add_handler(CommandHandler("rolar", rolar))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("cargo", cargo))
    app.add_handler(CallbackQueryHandler(definir_cargo, pattern='^(Infiltrador|Atirador|Negociador|Líder Tático)$'))
    app.add_handler(CommandHandler("sala_vip", sala_vip))
    app.add_handler(CommandHandler("cofre", cofre))

    # Rodar o bot e o servidor juntos sem criar um novo loop
    from threading import Thread
    Thread(target=run_web_server).start()
    await app.run_polling()

# Executa o bot
if __name__ == "__main__":
    main()  # Remover o asyncio.run e chamando diretamente a função main()