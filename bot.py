import json, os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Dummy web server for Render free tier
class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Live!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), MyHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

TOKEN = os.getenv("TOKEN")
DB = "videos.json"
seen_videos = set()

if os.path.exists(DB):
    try:
        seen_videos = set(json.load(open(DB)))
    except:
        seen_videos = set()

async def check_duplicate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post and update.channel_post.video:
        file_id = update.channel_post.video.file_unique_id
        if file_id in seen_videos:
            try:
                await context.bot.delete_message(chat_id=update.channel_post.chat_id, message_id=update.channel_post.message_id)
            except Exception as e:
                print(e)
        else:
            seen_videos.add(file_id)
            json.dump(list(seen_videos), open(DB, "w"))

app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, check_duplicate))
app.run_polling()
