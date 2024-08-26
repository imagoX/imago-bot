from telegram import Update
from telegram.ext import CallbackContext, ContextTypes
from telegram.error import BadRequest
from bot.utils.general_functions import is_user_admin
from bot.utils.general_constants import ALLOWED_GROUP_IDS

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        await update.message.reply_text("این گروه، گروه تایپولوژی نیست.")
        return

    if not await is_user_admin(update.message.chat.id, update.message.from_user.id, context):
        await update.message.reply_text("این دستور فقط برای ادمین‌ها قابل دسترسی است.")
        return

    admin = update.effective_user
    user_to_unban = None

    if update.message.reply_to_message:
        user_to_unban = update.message.reply_to_message.from_user
    elif context.args:
        if context.args[0].startswith('@'):
            username = context.args[0][1:]
            try:
                user_to_unban = await context.bot.get_chat(username)
            except BadRequest:
                await update.message.reply_text(f"کاربر با نام کاربری @{username} یافت نشد.")
                return
        else:
            user_id = context.args[0]
            try:
                user_to_unban = await context.bot.get_chat(user_id)
            except BadRequest:
                await update.message.reply_text(f"کاربر با شناسه {user_id} یافت نشد.")
                return

    if not user_to_unban:
        await update.message.reply_text(
            "لطفاً این دستور را در پاسخ به پیام کاربر مورد نظر استفاده کنید یا نام کاربری یا شناسه کاربر را مشخص کنید."
        )
        return

    if user_to_unban.id == context.bot.id:
        await update.message.reply_text("من نمی‌توانم خودم را آنبن کنم.")
        return

    try:
        await context.bot.unban_chat_member(
            chat_id=update.effective_chat.id, user_id=user_to_unban.id
        )
        await update.message.reply_text(
            f"کاربر [{user_to_unban.full_name}](tg://user?id={user_to_unban.id}) "
            f"توسط ادمین [{admin.full_name}](tg://user?id={admin.id}) آنبن شد.",
            parse_mode="Markdown",
        )
    except BadRequest as e:
        if "administrator" in str(e).lower():
            await update.message.reply_text("من نمی‌توانم یک ادمین را آنبن کنم.")
        else:
            await update.message.reply_text(
                "من نمی‌توانم کاربر را آنبن کنم. لطفاً از دسترسی من اطمینان حاصل کنید."
            )