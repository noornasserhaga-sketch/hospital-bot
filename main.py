import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("8531604454:AAGT7cKDaXStmXh1L2VGFq9FQLnFo6svWDY")

print("TOKEN_REPR:", repr(TOKEN), flush=True)
print("BOT_TOKEN_IN_ENV:", "BOT_TOKEN" in os.environ, flush=True)

if not TOKEN:
    raise ValueError("BOT_TOKEN is missing from environment")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("البوت شغال ✅")


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()


if __name__ == "__main__":
    main()
