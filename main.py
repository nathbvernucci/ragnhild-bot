import os
import threading
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from http.server import SimpleHTTPRequestHandler, HTTPServer

# Dicionário global de jogadores
jogadores = {}

# Máfias disponíveis
mafias = {
    'outfit': 'Outfit',
    'camorra': 'Camorra',
    'famiglia': 'Famiglia'
}

# Cargos disponíveis
cargos_disponiveis = [
    "Capo", "Consigliere", "Underboss", "Médico(a)", "Interrogador(a)",
    "Traficante", "Atirador(a)", "Estrategista", "Hacker", "Executor", "Soldado"
]

# Início do jogo
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Entrar na Outfit", callback_data='outfit')],
        [InlineKeyboardButton("Entrar na Camorra", callback_data='camorra')],
        [InlineKeyboardButton("Entrar na Famiglia", callback_data='famiglia')]
    ]
    await update.message.reply_text("Bem-vindo à Operação Ragnhild! Escolha sua máfia:", reply_markup=InlineKeyboardMarkup(keyboard))

# Seleção de máfia
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    escolha = query.data
    jogadores[user_id] = {
        "mafia": mafias[escolha],
        "vida": 100,
        "força": random.randint(5, 20),
        "pontuacao": 0
    }
    await query.answer()
    await query.edit_message_text(f"Você entrou na máfia {mafias[escolha]}.\nAgora use o comando /ficha para completar seu personagem.")

# Ficha de personagem
async def ficha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in jogadores:
        await update.message.reply_text("Use /start para escolher sua máfia antes de criar a ficha.")
        return
    texto = (
        "Preencha sua ficha da seguinte forma:\n\n"
        "*Nome*: (seu nome de personagem)\n"
        "*Cargo*: (escolha entre: Capo, Consigliere, Underboss, Médico(a), Interrogador(a), Traficante, Atirador(a), Estrategista, Hacker, Executor, Soldado)\n"
        "*Habilidade*: (descreva uma habilidade especial do seu personagem)\n\n"
        "Exemplo:\n"
        "Nome: Marco Ricci\n"
        "Cargo: Atirador\n"
        "Habilidade: Disparo preciso que ignora cobertura"
    )
    await update.message.reply_text(texto)

# Captura da ficha
async def ficha_preenchida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in jogadores:
        return
    texto = update.message.text
    linhas = texto.split('\n')
    if len(linhas) < 3:
        return
    try:
        nome = linhas[0].split(":")[1].strip()
        cargo = linhas[1].split(":")[1].strip()
        habilidade = linhas[2].split(":")[1].strip()
        jogadores[user_id]["nome"] = nome
        jogadores[user_id]["cargo"] = cargo
        jogadores[user_id]["habilidade"] = habilidade
        await update.message.reply_text(f"Ficha registrada com sucesso!\nNome: {nome}\nCargo: {cargo}\nHabilidade: {habilidade}")
    except:
        await update.message.reply_text("Erro ao processar a ficha. Certifique-se de seguir o formato corretamente.")

# Comando /status
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in jogadores:
        await update.message.reply_text("Use /start para começar.")
        return
    p = jogadores[user_id]
    await update.message.reply_text(
        f"MÁFIA: {p['mafia']}\n"
        f"VIDA: {p['vida']}\n"
        f"FORÇA: {p['força']}\n"
        f"NOME: {p.get('nome', 'N/D')}\n"
        f"CARGO: {p.get('cargo', 'N/D')}\n"
        f"HABILIDADE: {p.get('habilidade', 'N/D')}"
    )

# Comando /sala_vip
async def sala_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "*CENA: SALA VIP DO PALÁCIO RAGNHILD*\n\n"
        "O salão ecoa música clássica e brindes discretos. O embaixador está presente, mas também há algo de estranho no ar.\n"
        "Subitamente, um segurança desconfia de um dos convidados... é hora de agir.\n\n"
        "*Escolha da máfia:*\n"
        "1 - Interceptar o segurança silenciosamente.\n"
        "2 - Provocar um tumulto para distração.\n"
        "3 - Subornar um garçom e se aproximar do embaixador."
    )
    await update.message.reply_text(texto)

# Comando /cofre
async def cofre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "*CENA: SUBNÍVEL DO COFRE*\n\n"
        "Os sensores ainda estão ativos. Um grupo rival já tentou invadir, deixando destroços e sangue.\n"
        "O cofre está protegido por uma tranca biométrica e reconhecimento facial.\n\n"
        "*Escolha da máfia:*\n"
        "1 - Tentar hackear o sistema.\n"
        "2 - Usar um explosivo silencioso.\n"
        "3 - Tentar extrair os dados biométricos de um cadáver próximo."
    )
    await update.message.reply_text(texto)

# Comando /final
async def final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    pontos = jogadores.get(user_id, {}).get("pontuacao", 0)

    if pontos >= 70:
        texto = (
            "[PONTUAÇÃO ALTA – +70 pontos]\n\n"
            "*Diretriz Cinematográfica:*\n"
            "O golpe foi um sucesso. A Lança está em sua posse. O sistema de segurança foi neutralizado antes do alarme, e a rota de fuga está liberada.\n\n"
            "Agora escreva sua fuga. Como você atravessa o salão em ruínas? Leva a escultura consigo ou a disfarça?\n"
            "Onde seu veículo (ou helicóptero) o aguarda?\n"
            "Descreva sua cena final como em um filme: o salto, o disfarce, a explosão ou o silêncio absoluto…"
        )
    elif 40 <= pontos < 70:
        texto = (
            "[PONTUAÇÃO MÉDIA – 40 a 70 pontos]\n\n"
            "*Diretriz Cinematográfica:*\n"
            "Você conseguiu sair… mas não ileso. Um explosivo falhou. Um dos seus aliados está ferido.\n\n"
            "Agora escreva sua fuga. Carrega o ferido? Abandona a peça para salvar alguém?\n"
            "Tenta cruzar o túnel sob o jardim real ou improvisa uma saída pelos esgotos?\n"
            "Conte essa fuga com tensão, dor e estratégia. Tudo está em jogo."
        )
    else:
        texto = (
            "[PONTUAÇÃO BAIXA – Abaixo de 40 pontos]\n\n"
            "*Diretriz Cinematográfica:*\n"
            "O caos dominou tudo. Alarmes soaram antes da hora. A Lança de Salomão foi destruída no fogo cruzado.\n\n"
            "Agora escreva sua fuga. Você improvisa? Explode uma parede? Se rende e depois escapa em transporte hospitalar?\n"
            "Mostre o desespero, o sangue e a astúcia da sobrevivência."
        )

    await update.message.reply_text(texto)

# Dado
async def rolar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        arg = context.args[0]
        qtd, dado = map(int, arg.lower().split('d'))
        resultados = [random.randint(1, dado) for _ in range(qtd)]
        total = sum(resultados)
        await update.message.reply_text(f"Resultados: {resultados} | Total: {total}")
    except:
        await update.message.reply_text("Uso correto: /rolar 1d20")

# HTTP para Render
def run_http_server():
    server = HTTPServer(('0.0.0.0', 8080), SimpleHTTPRequestHandler)
    print("Servidor HTTP iniciado na porta 8080")
    server.serve_forever()

# Inicializa o bot
async def run_bot():
    from dotenv import load_dotenv
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler("ficha", ficha))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ficha_preenchida))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("rolar", rolar))
    app.add_handler(CommandHandler("sala_vip", sala_vip))
    app.add_handler(CommandHandler("cofre", cofre))
    app.add_handler(CommandHandler("final", final))

    await app.run_polling()

# Executa tudo
if __name__ == '__main__':
    threading.Thread(target=run_http_server).start()
    import asyncio
    asyncio.run(run_bot())