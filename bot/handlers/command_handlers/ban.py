from typing import Optional
from telegram import Update, User
from telegram.ext import ContextTypes
from telegram.error import BadRequest, TelegramError, Forbidden

from bot.utils.general_functions import is_user_admin
from bot.utils.general_constants import ALLOWED_GROUP_IDS

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        return

    if not await is_user_admin(update.message.chat.id, update.effective_user.id, context):
        await update.message.reply_text("این دستور فقط برای ادمین‌ها قابل دسترسی است.")
        return

    admin = update.effective_user
    reason = ""
    user_to_ban: Optional[User] = None

    if update.message.reply_to_message:
        user_to_ban = update.message.reply_to_message.from_user
        reason = " ".join(context.args) if context.args else "بدون دلیل"
    elif context.args:
        if context.args[0].startswith('@'):
            username = context.args[0][1:]
            try:
                user = await context.bot.get_chat(update.effective_chat.id)
                print(user)
                user_to_ban = user
                await update.message.reply_text(f"یافت شد: {user}")
            except BadRequest as e:
                await update.message.reply_text(f"خطا در یافتن کاربر @{username}: {str(e)}")
                return
        elif context.args[0].isdigit():
            user_id = int(context.args[0])
            try:
                user = await context.bot.get_chat(user_id)
                user_to_ban = user
            except BadRequest as e:
                await update.message.reply_text(f"خطا در یافتن کاربر با آیدی {user_id}: {str(e)}")
                return
        else:
            await update.message.reply_text("لطفاً نام کاربری را با @ یا آیدی عددی کاربر را وارد کنید.")
            return
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "بدون دلیل"
    else:
        await update.message.reply_text(
            "لطفاً این دستور را در پاسخ به پیام کاربر مورد نظر استفاده کنید یا نام کاربری یا آیدی کاربر را مشخص کنید."
        )
        return

    if not user_to_ban:
        await update.message.reply_text("کاربر مورد نظر یافت نشد.")
        return

    if user_to_ban.id == context.bot.id:
        await update.message.reply_text("من نمی‌توانم خودم را بن کنم.")
        return

    try:
        chat_member = await context.bot.get_chat_member(update.effective_chat.id, user_to_ban.id)
        if chat_member.status == 'left':
            await update.message.reply_text(f"کاربر {user_to_ban.full_name} در حال حاضر در گروه نیست.")
            return
        elif chat_member.status == 'kicked':
            await update.message.reply_text(f"کاربر {user_to_ban.full_name} قبلاً از گروه بن شده است.")
            return
    except BadRequest as e:
        await update.message.reply_text(f"خطا در بررسی وضعیت کاربر در گروه: {str(e)}")
        return

    try:
        await context.bot.ban_chat_member(
            chat_id=update.effective_chat.id, user_id=user_to_ban.id
        )
        await update.message.reply_text(
            f"کاربر [{user_to_ban.full_name}](tg://user?id={user_to_ban.id}) "
            f"توسط ادمین [{admin.full_name}](tg://user?id={admin.id}) بن شد.\n"
            f"دلیل: {reason}",
            parse_mode="Markdown",
        )
    except BadRequest as e:
        if "user is an administrator" in str(e).lower():
            await update.message.reply_text("من نمی‌توانم یک ادمین را بن کنم.")
        else:
            await update.message.reply_text(
                f"من نمی‌توانم کاربر را بن کنم. لطفاً از دسترسی من اطمینان حاصل کنید. خطا: {e}"
            )
    except Forbidden as e:
        await update.message.reply_text(
            f"من دسترسی کافی برای بن کردن کاربر ندارم. لطفاً مطمئن شوید که من ادمین هستم و دسترسی بن کردن دارم. خطا: {e}"
        )
    except TelegramError as e:
        await update.message.reply_text(
            f"خطای عمومی تلگرام رخ داد: {e}"
        )