from telegram import Update
from telegram.ext import CallbackContext

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "در حال اجرا هستم. برای راهنمایی بیشتر دستور /help را وارد کنید."
    )