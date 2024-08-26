from telegram import Update
from telegram.ext import CallbackContext
from bot.utils.general_functions import is_user_admin
from bot.utils.general_constants import ALLOWED_GROUP_IDS
import logging

async def unpin_all_messages(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        return

    if not await is_user_admin(
        update.message.chat.id, update.message.from_user.id, context
    ):
        await update.message.reply_text("این دستور فقط برای ادمین‌ها قابل دسترسی است.")
        return

    try:
        await update.message.chat.unpin_all_messages()
    except Exception as e:
        logging.error(f"Error unpinning messages: {e}")
        await update.message.reply_text("خطایی در از سنجاق خارج کردن پیام‌ها رخ داد.")