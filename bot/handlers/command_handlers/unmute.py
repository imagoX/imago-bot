from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus
from telegram.error import BadRequest
import logging
from bot.utils.general_constants import ALLOWED_GROUP_IDS

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        await update.message.reply_text("این گروه، گروه تایپولوژی نیست.")
        return

    admin = update.effective_user
    chat_member = await context.bot.get_chat_member(update.effective_chat.id, admin.id)
    if chat_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await update.message.reply_text("این دستور فقط برای ادمین‌ها قابل دسترسی است.")
        return
    
    args = context.args
    if args and args[0].startswith('@'):
        username = args[0][1:]
        try:
            user = await context.bot.get_chat_member(update.effective_chat.id, username)
            target_user = user.user
        except BadRequest:
            await update.message.reply_text(f"کاربر با نام کاربری @{username} در این گروه یافت نشد.")
            return
    elif update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    else:
        await update.message.reply_text(
            "لطفاً این دستور را در پاسخ به پیام کاربر مورد نظر استفاده کنید یا نام کاربری را بعد از دستور وارد کنید."
        )
        return

    if target_user.id == context.bot.id:
        await update.message.reply_text("من نمی‌توانم خودم را آنمیوت کنم.")
        return

    try:
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=target_user.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_polls=False,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False,
            ),
        )
        await update.message.reply_text(
            f"کاربر [{target_user.full_name}](tg://user?id={target_user.id}) "
            f"توسط ادمین [{admin.full_name}](tg://user?id={admin.id}) آنمیوت شد.",
            parse_mode="Markdown",
        )
    except BadRequest as e:
        if "user is an administrator" in str(e).lower():
            await update.message.reply_text("من نمی‌توانم یک ادمین را آنمیوت کنم.")
        else:
            logging.error(f"Error unmuting user: {e}")
            await update.message.reply_text(
                "خطایی در آنمیوت کردن کاربر رخ داد. لطفاً از دسترسی من اطمینان حاصل کنید."
            )