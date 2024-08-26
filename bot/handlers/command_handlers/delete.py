from telegram import Update
from telegram.ext import CallbackContext
from telegram.error import TelegramError
from telegram.constants import ChatMemberStatus
from bot.utils.general_constants import ALLOWED_GROUP_IDS
import logging

async def delete_message(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        return

    admin = update.effective_user
    chat_member = await context.bot.get_chat_member(update.effective_chat.id, admin.id)

    if chat_member.status not in [
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER,
    ]:
        await update.message.reply_text("این دستور فقط برای ادمین‌ها قابل دسترسی است.")
        return

    if update.message.reply_to_message:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.reply_to_message.message_id,
            )
        except TelegramError as e:
            logging.error(f"Error deleting message: {e}")
            await update.message.reply_text("خطایی در حذف پیام رخ داد.")