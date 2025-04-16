import os
import asyncio
import random
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

jogadores = {}
fichas = {}
pontuacoes = {"Outfit": 0, "Camorra": 0, "Famiglia": 0}

cargos = [
    "Capo", "Consigliere", "Underboss", "Médico(a)", "Interrogador(a)",
    "Traficante", "Atirador(a)", "Estrategista", "Hacker", "Executor", "Soldado"
]

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Entrar na Outfit", callback_data='Outfit')],
        [InlineKeyboardButton("Entrar na Camorra", callback_data='Camorra')],
        [InlineKeyboardButton("Entrar na Famiglia", callback_data='Famiglia')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Escolha sua máfia:", reply_markup=reply_markup)

# Botão de escolha de máfia
async def escolher_mafia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    escolha = query.data
    jogadores[user_id] = {"mafia": escolha, "vida": 100, "força": random.randint(5, 20)}
    await query.edit_message_text(f"Você entrou na máfia {escolha}.\nUse /ficha para montar sua ficha.")

# Comando /ficha
async def ficha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in jogadores:
        await update.message.reply_text("Use /start para escolher sua máfia primeiro.")
        return
    fichas[user_id] = {"passo": "nome"}
    await update.message.reply_text("Digite o **nome do seu personagem**:")

# Coletar informações da ficha
async def coletar_ficha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in fichas:
        return

    ficha = fichas[user_id]
    texto = update.message.text

    if ficha["passo"] == "nome":
        ficha["nome"] = texto
        ficha["passo"] = "cargo"
        cargos_str = ", ".join(cargos)
        await update.message.reply_text(f"Escolha o **cargo na máfia** entre:\n{cargos_str}")
    elif ficha["passo"] == "cargo":
        if texto not in cargos:
            await update.message.reply_text("Cargo inválido. Escolha novamente.")
            return
        ficha["cargo"] = texto
        ficha["passo"] = "habilidade"
        await update.message.reply_text("Descreva a **habilidade especial** do seu personagem:")
    elif ficha["passo"] == "habilidade":
        ficha["habilidade"] = texto
        ficha["passo"] = None
        await update.message.reply_text("Ficha concluída!\nUse /status para ver seus dados.")
    fichas[user_id] = ficha

# Comando /status
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in jogadores:
        info = jogadores[user_id]
        ficha = fichas.get(user_id, {})
        resposta = (
            f"MÁFIA: {info['mafia']}\n"
            f"VIDA: {info['vida']}\n"
            f"FORÇA: {info['força']}\n"
            f"NOME: {ficha.get('nome', '—')}\n"
            f"CARGO: {ficha.get('cargo', '—')}\n"
            f"HABILIDADE: {ficha.get('habilidade', '—')}"
        )
        await update.message.reply_text(resposta)
    else:
        await update.message.reply_text("Você ainda não escolheu uma máfia. Use /start.")

# Comando /rolar 1d20
async def rolar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        arg = context.args[0]
        qtd, dado = map(int, arg.lower().split('d'))
        resultados = [random.randint(1, dado) for _ in range(qtd)]
        total = sum(resultados)
        await update.message.reply_text(f"Resultados: {resultados} | Total: {total}")
    except:
        await update.message.reply_text("Uso correto: /rolar 1d20")

# Comando /vip
async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Você entra na sala VIP. O som abafado da música clássica contrasta com o brilho das joias e armas escondidas.\n"
        "O embaixador sorri ao te ver se aproximar.\n\n"
        "Escolha:\n1 - Se aproximar com charme\n2 - Subornar os seguranças\n3 - Ameaçar discretamente"
    )

# Comando /cofre
async def cofre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Você alcança a porta do cofre. O painel eletrônico exige precisão.\n\n"
        "Escolha:\n1 - Hackear o painel\n2 - Explodir com C4\n3 - Usar a chave roubada do diretor"
    )

# Comando /pontuacao
async def pontuacao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = "\n".join([f"{mafia}: {pontos}" for mafia, pontos in pontuacoes.items()])
    await update.message.reply_text(f"Pontuação atual:\n{texto}")

# Função principal
async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(escolher_mafia))
    app.add_handler(CommandHandler("ficha", ficha))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, coletar_ficha))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("rolar", rolar))
    app.add_handler(CommandHandler("vip", vip))
    app.add_handler(CommandHandler("cofre", cofre))
    app.add_handler(CommandHandler("pontuacao", pontuacao))
    print("Bot rodando... aguardando comandos.")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())