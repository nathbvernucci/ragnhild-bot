import os
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import random
from http.server import SimpleHTTPRequestHandler, HTTPServer

# Dicionário temporário para armazenar status dos jogadores
jogadores = {}
pontuacoes = {"Outfit": 0, "Camorra": 0, "Famiglia": 0}  # Pontuação das máfias

# Cargos possíveis
cargos = [
    "Capo", "Consigliere", "Underboss", "Médico(a)", "Interrogador(a)", 
    "Traficante", "Atirador(a)", "Estrategista", "Hacker", "Executor", "Soldado"
]

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Entrar na Outfit", callback_data='Outfit'),
            InlineKeyboardButton("Entrar na Camorra", callback_data='Camorra'),
            InlineKeyboardButton("Entrar na Famiglia", callback_data='Famiglia'),
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

# Comando para o jogador escolher o cargo
async def cargo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in jogadores:
        await update.message.reply_text("Você precisa escolher uma máfia primeiro usando /start!")
        return
    jogador = jogadores[user_id]
    if jogador['cargo'] is not None:
        await update.message.reply_text(f"Você já escolheu o cargo: {jogador['cargo']}")
        return
    
    # Mostra os cargos disponíveis para o jogador escolher
    keyboard = [[InlineKeyboardButton(cargo, callback_data=cargo)] for cargo in cargos]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Escolha seu cargo:", reply_markup=reply_markup)

# Função para definir o cargo do jogador
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

# Função da Sala VIP
async def sala_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in jogadores:
        await update.message.reply_text("Você precisa escolher uma máfia antes de acessar a sala VIP!")
        return

    jogador = jogadores[user_id]
    mafia = jogador['mafia']

    descricao = f"Você está na sala VIP. Seu objetivo é reunir informações importantes, mas a segurança está forte. Escolha sabiamente!"
    keyboard = [
        [InlineKeyboardButton("Tentar acessar a sala VIP", callback_data='entrar_vip')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(descricao, reply_markup=reply_markup)

# Função de acessar a sala VIP
async def entrar_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in jogadores:
        await query.edit_message_text("Você ainda não escolheu uma máfia.")
        return

    jogador = jogadores[user_id]
    mafia = jogador['mafia']

    resultado = random.randint(1, 20) + jogador['força']

    if resultado > 15:
        # Sucesso
        pontos = random.randint(5, 15)
        pontuacoes[mafia] += pontos
        await query.edit_message_text(f"Você conseguiu acessar a sala VIP e obteve {pontos} pontos para a {mafia.upper()}.")
    else:
        # Falha
        jogador['vida'] -= 10
        pontuacoes[mafia] -= 5
        await query.edit_message_text(f"Você falhou em acessar a sala VIP e perdeu 10 pontos de vida. A {mafia.upper()} perdeu 5 pontos.")

# Função do Cofre
async def cofre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in jogadores:
        await update.message.reply_text("Você precisa escolher uma máfia antes de acessar o cofre!")
        return

    jogador = jogadores[user_id]
    mafia = jogador['mafia']

    descricao = f"Você está na sala do cofre. O objetivo é acessar o cofre e pegar o loot. A segurança está alta. Você precisa da chave certa!"
    keyboard = [
        [InlineKeyboardButton("Tentar abrir o cofre", callback_data='abrir_cofre')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(descricao, reply_markup=reply_markup)

# Função de abrir o cofre
async def abrir_cofre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in jogadores:
        await query.edit_message_text("Você ainda não escolheu uma máfia.")
        return

    jogador = jogadores[user_id]
    mafia = jogador['mafia']

    resultado = random.randint(1, 20) + jogador['força']

    if resultado > 15:
        loot = random.randint(10, 50)  # A quantidade de loot roubado
        pontuacoes[mafia] += loot
        await query.edit_message_text(f"Você conseguiu abrir o cofre e roubou {loot} pontos! A {mafia.upper()} está mais rica.")
    else:
        jogador['vida'] -= 15
        pontuacoes[mafia] -= 10
        await query.edit_message_text(f"Você falhou em abrir o cofre e perdeu 15 pontos de vida. A {mafia.upper()} perdeu 10 pontos.")

# Comando para ver a pontuação
async def pontuacao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pontuacao_atual = "\n".join([f"{mafia}: {pontos}" for mafia, pontos in pontuacoes.items()])
    await update.message.reply_text(f"Pontuação atual das máfias:\n{pontuacao_atual}")

# Função para rodar o servidor HTTP simples
def run_http_server():
    server = HTTPServer(('0.0.0.0', 8080), SimpleHTTPRequestHandler)
    print("Servidor HTTP iniciado na porta 8080")
    server.serve_forever()

# Função para rodar o bot em uma thread separada
async def run_bot():
    from dotenv import load_dotenv
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler("rolar", rolar))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("cargo", cargo))  # Adiciona o comando para escolher cargo
    app.add_handler(CallbackQueryHandler(definir_cargo, pattern='^[A-Za-z ]+$'))  # Define o cargo
    app.add_handler(CommandHandler("sala_vip", sala_vip))  # Acesso à sala VIP
    app.add_handler(CallbackQueryHandler(entrar_vip, pattern='entrar_vip'))  # Ação para entrar na sala VIP
    app.add_handler(CommandHandler("cofre", cofre))  # Comando para acessar o cofre
    app.add_handler(CallbackQueryHandler(abrir_cofre, pattern='abrir_cofre'))  # Ação para abrir o cofre
    app.add_handler(CommandHandler("pontuacao", pontuacao))  # Exibe a pontuação das máfias

    await app.run_polling()

# Rodando o servidor HTTP e o bot
if __name__ == "__main__":
    threading.Thread(target=run_http_server).start()

    import asyncio
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    loop.run_forever()