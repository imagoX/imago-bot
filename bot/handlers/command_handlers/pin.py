from telegram import Update
from telegram.ext import CallbackContext
from telegram.error import TelegramError
from bot.utils.general_functions import is_user_admin
from bot.utils.general_constants import ALLOWED_GROUP_IDS
import logging

async def pin_message(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        return

    if not await is_user_admin(
        update.message.chat.id, update.message.from_user.id, context
    ):
        await update.message.reply_text("این دستور فقط برای ادمین‌ها قابل دسترسی است.")
        return

    if update.message.reply_to_message:
        try:
            await update.message.reply_to_message.pin()
        except Exception as e:
            logging.error(f"Error pinning message: {e}")
            await update.message.reply_text("خطایی در سنجاق کردن پیام رخ داد.")
    else:
        await update.message.reply_text(
            "این دستور باید با ریپلای به پیام کاربر ارسال شود."
        )