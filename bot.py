import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")

# Already posted video IDs
seen_videos = set()

async def check_duplicate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post and update.channel_post.video:
        file_id = update.channel_post.video.file_unique_id
        if file_id in seen_videos:
            try:
                await context.bot.delete_message(
                    chat_id=update.channel_post.chat_id,
                    message_id=update.channel_post.message_id
                )
            except Exception as e:
                print(f"Delete failed: {e}")
        else:
            seen_videos.add(file_id)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.VIDEO, check_duplicate))
    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
