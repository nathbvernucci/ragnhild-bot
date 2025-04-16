import os
import random
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
        "*Operação Ragnhild* está prestes a começar...\n\n"
        "A sala está silenciosa, a tensão no ar é palpável. Cada movimento é um risco, cada escolha, uma jogada de mestre."
        "\nVocê está prestes a entrar no coração da noite, onde facções rivais e segredos são moeda corrente.\n\n"
        "Escolha sua máfia e prepare-se para a maior jogada de sua vida...",
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
    await query.edit_message_text(f"A brisa gélida passa sobre você enquanto a {escolha.upper()} marca seu território. O destino de todos os jogadores agora está entre suas mãos.")

# /rolar
async def rolar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        arg = context.args[0]
        qtd, faces = map(int, arg.lower().split('d'))
        resultados = [random.randint(1, faces) for _ in range(qtd)]
        total = sum(resultados)
        await update.message.reply_text(f"Você rolou: {resultados} | Total: {total}")
    except Exception:
        await update.message.reply_text("Erro na rolagem! Use o formato: /rolar 1d20")

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
        await update.message.reply_text("Escolha sua máfia primeiro com /start.")

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
    await update.message.reply_text("A tensão no ar aumenta. Escolha seu cargo e mostre seu valor:", reply_markup=InlineKeyboardMarkup(keyboard))

# Callback para definir cargo
async def definir_cargo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cargo = query.data
    user_id = query.from_user.id
    if user_id in jogadores:
        jogadores[user_id]['cargo'] = cargo
        await query.edit_message_text(f"Cargo definido: {cargo} - Agora, sua missão está mais clara do que nunca.")
    else:
        await query.edit_message_text("Escolha uma máfia primeiro com /start.")

# /sala_vip
async def sala_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in jogadores:
        await update.message.reply_text("Escolha sua máfia primeiro com /start.")
        return
    texto = "Você avança pela entrada secreta. Um leve som metálico ecoa pelo corredor. O embaixador está lá dentro, mas as portas estão fechadas. Você vai tentar?"
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
        await query.edit_message_text(f"Você adentra a sala com a frieza de um caçador. Com precisão cirúrgica, garante {pontos} pontos para a {mafia.upper()}.")
    else:
        jogador['vida'] -= 10
        pontuacoes[mafia] -= 5
        await query.edit_message_text(f"O fracasso é amargo. Sua infiltração foi comprometida! -10 de vida. A {mafia.upper()} perdeu 5 pontos.")

# /cofre
async def cofre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in jogadores:
        await update.message.reply_text("Escolha sua máfia primeiro com /start.")
        return
    keyboard = [[InlineKeyboardButton("Abrir Cofre", callback_data='abrir_cofre')]]
    await update.message.reply_text("Você chega diante do cofre. A combinação da vida ou da morte está ao seu alcance. Vai tentar?", reply_markup=InlineKeyboardMarkup(keyboard))

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
        await query.edit_message_text(f"Com precisão letal, o cofre se abre. O que você encontra são {loot} pontos de riqueza para a {mafia.upper()}.")
    else:
        jogador['vida'] -= 15
        pontuacoes[mafia] -= 10
        await query.edit_message_text(f"O cofre está fechado. Você falha e sofre os danos do erro! -15 de vida. {mafia.upper()} perde 10 pontos.")

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
        final = "Vitória Suprema: sua fuga é impecável, você sai em um carro blindado enquanto o palácio explode ao fundo."
    elif 40 <= pontos < 70:
        final = "Final Intermediário: seu nome será lembrado, mas não sem sacrifícios. A fuga é tumultuada, mas você escapa."
    else:
        final = "Final Trágico: a perseguição é implacável. Você é forçado a fugir pelas ruas escuras, ferido, mas vivo."

    await update.message.reply_text(f"Final da {jogador['mafia'].upper()}:\n{final}")

# === Funções de Execução ===

# Rodar servidor web básico para manter Render ativo
def run_web_server():
    port = int(os.environ.get("PORT", 10000))  # Usa a porta que o Render libera
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    print(f"Servidor web rodando na porta {port}")
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