import os, json
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TOKEN")
DB_FILE = "videos.json"

# load old database
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        videos = set(json.load(f))
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
        except:
            pass
        return
    
    videos.add(file_id)
    with open(DB_FILE, "w") as f:
        json.dump(list(videos), f)

app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, check_duplicate))
app.run_polling()
