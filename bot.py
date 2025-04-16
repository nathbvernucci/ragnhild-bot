import threading
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Olá, estou rodando!')

def run_bot():
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    if not BOT_TOKEN:
        print("Erro: BOT_TOKEN não definido")
        return

    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    print("Bot rodando...")
    updater.start_polling()

def run_http_server():
    from http.server import HTTPServer, BaseHTTPRequestHandler

    class SimpleHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Bot funcionando")

    server = HTTPServer(('0.0.0.0', 8080), SimpleHandler)
    print("Servidor HTTP na porta 8080...")
    server.serve_forever()

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    threading.Thread(target=run_http_server).start()
