import os, json, threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest

TOKEN = os.environ.get("TOKEN")
DB_FILE = "videos.json"

# --- Web Service er jonno port kholar trick (Free te) ---
app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "Bot is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host='0.0.0.0', port=port)

threading.Thread(target=run_flask, daemon=True).start()
# --- End ---

if os.path.exists(DB_FILE):
    try:
        with open(DB_FILE, "r") as f:
            videos = set(json.load(f))
    except:
        videos = set()
else:
    videos = set()

async def check_duplicate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.channel_post:
        return
    file_id = None
    if update.channel_post.video:
        file_id = update.channel_post.video.file_id
    elif update.channel_post.photo:
        file_id = update.channel_post.photo[-1].file_id
    elif update.channel_post.document:
        file_id = update.channel_post.document.file_id
    if not file_id:
        return
    chat_id = update.channel_post.chat.id
    message_id = update.channel_post.message_id
    if file_id in videos:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            print(f"DELETED: {message_id}")
        except Exception as e:
            print(f"Delete Failed (Admin?): {e}")
        return
    videos.add(file_id)
    with open(DB_FILE, "w") as f:
        json.dump(list(videos), f)

def main():
    request = HTTPXRequest(connect_timeout=30.0, read_timeout=60.0)
    app = Application.builder().token(TOKEN).request(request).build()
    app.add_handler(MessageHandler(filters.ALL, check_duplicate))
    print("Auto Delete Bot Started...")
    app.run_polling(drop_pending_updates=True, allowed_updates=["channel_post"])

if __name__ == "__main__":
    main()