import json, os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
TOKEN = os.getenv("TOKEN")
DB="videos.json"
seen=json.load(open(DB)) if os.path.exists(DB) else []
async def check(update, context):
    msg=update.channel_post
    if not msg or not (msg.video or msg.document): return
    fid=msg.video.file_unique_id if msg.video else msg.document.file_unique_id
    if fid in seen:
        try: await context.bot.delete_message(msg.chat_id, msg.message_id)
        except: pass
    else:
        seen.append(fid); json.dump(seen, open(DB,"w"))
app=Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, check))
app.run_polling()
