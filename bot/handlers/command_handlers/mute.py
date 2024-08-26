from datetime import datetime, timedelta
import logging
from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus
from telegram.error import BadRequest
from bot.utils.general_constants import ALLOWED_GROUP_IDS

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        await update.message.reply_text("این گروه، گروه تایپولوژی نیست.")
        return

    admin = update.effective_user
    chat_member = await context.bot.get_chat_member(update.effective_chat.id, admin.id)
    if chat_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await update.message.reply_text("این دستور فقط برای ادمین‌ها قابل دسترسی است.")
        return

    user_to_mute = None
    mute_duration = None
    args = context.args

    if update.message.reply_to_message:
        user_to_mute = update.message.reply_to_message.from_user
        if args:
            try:
                mute_duration = int(args[0])
            except ValueError:
                await update.message.reply_text("لطفاً یک عدد صحیح برای مدت میوت وارد کنید (به دقیقه).")
                return
    elif args:
        if args[0].startswith('@'):
            username = args[0][1:]
            try:
                user = await context.bot.get_chat(username)
                user_to_mute = user
                if len(args) > 1:
                    try:
                        mute_duration = int(args[1])
                    except ValueError:
                        await update.message.reply_text("لطفاً یک عدد صحیح برای مدت میوت وارد کنید (به دقیقه).")
                        return
            except BadRequest:
                await update.message.reply_text(f"کاربر با نام کاربری @{username} یافت نشد.")
                return
        else:
            await update.message.reply_text("لطفاً نام کاربری را با @ مشخص کنید.")
            return

    if not user_to_mute:
        await update.message.reply_text(
            "لطفاً این دستور را در پاسخ به پیام کاربر مورد نظر استفاده کنید یا نام کاربری را مشخص کنید."
        )
        return

    if user_to_mute.id == context.bot.id:
        await update.message.reply_text("من نمی‌توانم خودم را میوت کنم.")
        return

    until_date = datetime.now() + timedelta(minutes=mute_duration) if mute_duration else None

    try:
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=user_to_mute.id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
            ),
            until_date=until_date,
        )

        duration_text = f" به مدت {mute_duration} دقیقه" if mute_duration else " به صورت نامحدود"
        await update.message.reply_text(
            f"کاربر [{user_to_mute.full_name}](tg://user?id={user_to_mute.id}) "
            f"توسط ادمین [{admin.full_name}](tg://user?id={admin.id}){duration_text} میوت شد.",
            parse_mode="Markdown",
        )
    except BadRequest as e:
        if "user is an administrator" in str(e).lower():
            await update.message.reply_text("من نمی‌توانم یک ادمین را میوت کنم.")
        else:
            logging.error(f"Error muting user: {e}")
            await update.message.reply_text(
                "خطایی در میوت کردن کاربر رخ داد. لطفاً از دسترسی من اطمینان حاصل کنید."
            )