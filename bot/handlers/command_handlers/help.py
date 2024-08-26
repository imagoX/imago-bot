from telegram import Update
from telegram.ext import CallbackContext
from bot.utils.general_functions import is_allowed_group

async def help(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        f"درود، {update.message.from_user.full_name}\n\n"
        f"من Typology Bot v2.1 هستم.\n\n"
        f"برای استفاده، من را به گروه خود با دسترسی‌های معمولی ادمین "
        f"اضافه کنید، "
        f"در غیر این صورت، نمی‌توانم کار کنم.\n\n\n"
        f"دستورات برای ادمین‌ها:\n\n"
        f"<code>/ban</code> (دلیل) - بن کردن کاربر و حذف او از گروه\n\n"
        f"<code>/unban</code> - آنبن کردن\n\n"
        f"<code>/mute</code> - میوت کردن\n\n"
        f"<code>/mute 10m</code> - میوت کردن کاربر در زمان مشخص شده - 30m, 2h, 1d\n\n"
        f"<code>/unmute</code> - آنمیوت کردن\n\n"
        f"<code>/del</code> - حذف پیام\n\n"
        f"<code>/del 10</code> - حذف 10 پیام\n\n"
        f"<code>/report</code> - گزارش به ادمین‌ها\n\n"
        f"<code>/pin</code> - سنجاق کردن پیام\n\n"
        f"<code>/unpin</code> - از سنجاق خارج کردن\n\n"
        f"<code>/unpin_all</code> - از سنجاق خارج کردن همه پیام‌ها\n\n"
        f"توجه: تمام دستورات به جز آخری باید با پاسخ به پیام کاربر ارسال شوند!\n\n"
        f"<code>/admins</code> - نمایش همه ادمین‌ها\n\n\n"
        f"<code>/chat</code> - چت با بات\n\n"
        f"<code>/image</code> - ساخت عکس\n\n"
        f"با فرستادن لینک یوتیوب، به صورت خودکار دانلود می شود.\n"
        f"با فرستادن موزیک، دمو به صورت خودکار ایجاد می شود.\n\n\n"
        f"<i>Developed by imago</i>",
        parse_mode="HTML",
    )

    if not is_allowed_group(update.message.chat.id):
        return