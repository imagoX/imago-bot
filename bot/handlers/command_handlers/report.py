from telegram import Update
from telegram.ext import CallbackContext
from bot.utils.general_constants import ALLOWED_GROUP_IDS
import logging

async def report(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        await update.message.reply_text("این گروه، گروه تایپولوژی نیست.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text(
            "این دستور باید با ریپلای به پیام کاربر ارسال شود."
        )
        return

    reported_user = update.message.reply_to_message.from_user
    reported_by = update.message.from_user

    reported_user_chat_member = await context.bot.get_chat_member(
        update.effective_chat.id, reported_user.id
    )
    if reported_user_chat_member.status in ("administrator", "creator"):
        await update.message.reply_text("نمی‌توانید یک ادمین را گزارش دهید.")
        return

    if reported_user.id == reported_by.id:
        await update.message.reply_text("نمی‌توانید خودتان را گزارش دهید.")
        return

    admins = await context.bot.get_chat_administrators(update.effective_chat.id)

    admin_mentions = [
        f"[ ](tg://user?id={admin.user.id})"
        for admin in admins
        if not admin.user.is_bot
    ]

    try:
        admin_mentions_text = "".join(admin_mentions)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"{admin_mentions_text}\n"
            f"کاربر "
            f"[{reported_user.full_name}](tg://user?id={reported_user.id}) گزارش شد.",
            parse_mode="Markdown",
        )
        await update.message.reply_text("گزارش شما ارسال شد.")
    except Exception as e:
        logging.error(f"Error reporting user: {e}")
        await update.message.reply_text("خطایی در گزارش کاربر رخ داد.")