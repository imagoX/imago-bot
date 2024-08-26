from telegram import Update
from telegram.ext import CallbackContext, ContextTypes
from bot.utils.general_constants import ALLOWED_GROUP_IDS
import logging

async def get_admins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        await update.message.reply_text("این گروه، گروه تایپولوژی نیست.")
        return
    try:
        admins = await context.bot.get_chat_administrators(update.effective_chat.id)
        admin_info = []
        for admin in admins:
            status = "creator" if admin.status == "creator" else "admin"
            admin_info.append(f"{admin.user.full_name} - {status}")
        admin_list = "\n".join(admin_info)
        await update.message.reply_text(f"ادمین‌های در گروه:\n{admin_list}")
    except Exception as e:
        logging.error(f"Error getting admins: {e}")
        await update.message.reply_text("خطایی در نمایش ادمین‌ها رخ داد.")


async def my_info(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        await update.message.reply_text("این گروه، گروه تایپولوژی نیست.")
        return
    await update.message.reply_text(
        f"نام: {update.message.from_user.full_name}\n"
        f"آیدی: {update.message.from_user.id}\n"
        f"زبان: {update.message.from_user.language_code}\n"
        f"نام کاربری: {update.message.from_user.username}"
    )

async def chat_info(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        f"نام گروه: {update.message.chat.title}\n"
        f"آیدی گروه: {update.message.chat.id}\n"
        f"نوع گروه: {update.message.chat.type}"
    )