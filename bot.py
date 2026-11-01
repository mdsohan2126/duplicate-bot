import os, json, asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
from telegram.error import TimedOut, NetworkError

TOKEN = os.environ.get("TOKEN")
DB_FILE = "videos.json"

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
            print(f"Deleted duplicate: {message_id}")
        except Exception as e:
            print(f"Delete failed: {e}")
        return
    videos.add(file_id)
    with open(DB_FILE, "w") as f:
        json.dump(list(videos), f)

async def error_handler(update, context):
    err = str(context.error)
    print(f"Ignoring error: {err}")
    if "Timed out" in err or "TimedOut" in err:
        await asyncio.sleep(5)

def main():
    request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=60.0,
        write_timeout=30.0,
        pool_timeout=60.0
    )
    app = Application.builder().token(TOKEN).request(request).build()
    app.add_handler(MessageHandler(filters.ALL, check_duplicate))
    app.add_error_handler(error_handler)
    
    # Auto-restart loop, jate Render e kokhono off na hoy
    while True:
        try:
            print("Bot Started...")
            app.run_polling(
                drop_pending_updates=True,
                allowed_updates=["channel_post"],
                timeout=60,
                poll_interval=5.0
            )
        except (TimedOut, NetworkError) as e:
            print(f"Network timeout, restarting in 5s: {e}")
            import time
            time.sleep(5)
            continue
        except Exception as e:
            print(f"Crashed, restarting in 10s: {e}")
            import time
            time.sleep(10)
            continue

if __name__ == "__main__":
    main()
