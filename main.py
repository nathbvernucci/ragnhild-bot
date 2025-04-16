import os
import random
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Dicionário temporário para armazenar status dos jogadores
jogadores = {}
pontuacoes = {"Outfit": 0, "Camorra": 0, "Famiglia": 0}
cargos = ["Infiltrador", "Atirador", "Negociador", "Líder Tático"]

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("Entrar na Outfit", callback_data='Outfit'),
        InlineKeyboardButton("Entrar na Camorra", callback_data='Camorra'),
        InlineKeyboardButton("Entrar na Famiglia", callback_data='Famiglia'),
    ]]
    await update.message.reply_text(
        "Bem-vindo à *Operação Ragnhild*!\n\nO ar está denso e as sombras se estendem. A guerra entre as máfias está prestes a começar."
        "\n\nEscolha sua máfia e prepare-se para fazer sua marca nesse jogo de poder e traição.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
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
        await update.message.reply_text(f"Você rolou: {resultados} | Total: {total}. A sorte está lançada.")
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
        await update.message.reply_text("Use /start para escolher sua máfia primeiro.")
        return
    jogador = jogadores[user_id]
    if jogador['cargo']:
        await update.message.reply_text(f"Você já tem um cargo: {jogador['cargo']}.")
        return
    keyboard = [[InlineKeyboardButton(c, callback_data=c)] for c in cargos]
    await update.message.reply_text(
        "Escolha seu cargo para as missões decisivas!",
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
            text=f"Você agora é um {cargo}. Seu papel será essencial nas próximas decisões."
        )
    else:
        await query.edit_message_text(text="Escolha uma máfia antes de receber um cargo!")

# Sala VIP
async def sala_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in jogadores:
        await update.message.reply_text("Escolha sua máfia antes de acessar a sala VIP!")
        return
    descricao = (
        "Você se aproxima da Sala VIP. O cheiro de charutos caros, a tensão no ar... Há algo estranho. A segurança aumentou.\n"
        "Você quer arriscar entrar e buscar vantagem para sua máfia?"
    )
    keyboard = [[InlineKeyboardButton("Tentar entrar na sala VIP", callback_data='entrar_vip')]]
    await update.message.reply_text(descricao, reply_markup=InlineKeyboardMarkup(keyboard))

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
        await query.edit_message_text(
            f"Você entrou na Sala VIP e descobriu segredos valiosos. A {mafia.upper()} ganhou {pontos} pontos!"
        )
    else:
        jogador['vida'] -= 10
        pontuacoes[mafia] -= 5
        await query.edit_message_text(
            f"Falha! A segurança te feriu. -10 de vida. A {mafia.upper()} perdeu 5 pontos."
        )

# Cofre
async def cofre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in jogadores:
        await update.message.reply_text("Escolha sua máfia antes de tentar abrir o cofre!")
        return
    descricao = (
        "Você está diante do cofre principal. A tranca pisca. A tensão é absoluta. Você decide agir?"
    )
    keyboard = [[InlineKeyboardButton("Tentar abrir o cofre", callback_data='abrir_cofre')]]
    await update.message.reply_text(descricao, reply_markup=InlineKeyboardMarkup(keyboard))

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
        await query.edit_message_text(
            f"Sucesso! Você abriu o cofre e garantiu {loot} pontos para a {mafia.upper()}!"
        )
    else:
        jogador['vida'] -= 15
        pontuacoes[mafia] -= 10
        await query.edit_message_text(
            f"Alarme disparado! Você perdeu 15 de vida. A {mafia.upper()} perdeu 10 pontos."
        )

# Pontuação atual
async def pontuacao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = "\n".join([f"{mafia}: {pontos}" for mafia, pontos in pontuacoes.items()])
    await update.message.reply_text(f"Pontuação atual das máfias:\n\n{texto}")

# Final cinematográfico
async def final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in jogadores:
        await update.message.reply_text("Use /start para começar sua jornada.")
        return
    jogador = jogadores[user_id]
    mafia = jogador['mafia']
    pontos = pontuacoes[mafia]
    if pontos >= 70:
        texto = (
            f"A {mafia.upper()} emergiu como soberana incontestável.\n"
            "O ouro foi dividido, os inimigos esmagados. Você foge de helicóptero enquanto o Palácio Ragnhild ruía em chamas atrás de você.\n"
            "Final de Vitória Suprema."
        )
    elif 40 <= pontos < 70:
        texto = (
            f"A {mafia.upper()} conseguiu escapar, mas sofreu perdas.\n"
            "Você carrega a Lança de Salomão, mas sabe que a guerra ainda não acabou. O mundo verá vocês renascerem.\n"
            "Final Intermediário."
        )
    else:
        texto = (
            f"A {mafia.upper()} falhou. Tudo foi perdido.\n"
            "Você corre entre sirenes e fumaça, ferido, com apenas memórias do que poderia ter sido.\n"
            "Final Trágico."
        )
    await update.message.reply_text(texto)

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
    app.add_handler(CallbackQueryHandler(definir_cargo, pattern='^(Infiltrador|Atirador|Negociador|Líder Tático)$'))
    app.add_handler(CommandHandler("sala_vip", sala_vip))
    app.add_handler(CallbackQueryHandler(entrar_vip, pattern='entrar_vip'))
    app.add_handler(CommandHandler("cofre", cofre))
    app.add_handler(CallbackQueryHandler(abrir_cofre, pattern='abrir_cofre'))
    app.add_handler(CommandHandler("pontuacao", pontuacao))
    app.add_handler(CommandHandler("final", final))

    await app.run_polling()

# Servidor Web
def run_web_server():
    server = HTTPServer(('0.0.0.0', 8080), SimpleHTTPRequestHandler)
    server.serve_forever()

# Rodando o servidor web em uma thread separada e o bot normalmente
async def run():
    await main()

if __name__ == '__main__':
    import threading
    threading.Thread(target=run_web_server, daemon=True).start()
    asyncio.run(run())
    