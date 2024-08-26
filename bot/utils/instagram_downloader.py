import instaloader
import os
from telegram import Update
from telegram.ext import ContextTypes


def download_instagram_post(url: str, username: str) -> str:
    L = instaloader.Instaloader()
    shortcode = url.split("/")[-2]
    post = instaloader.Post.from_shortcode(L.context, shortcode)
    L.download_post(post, target=username)
    return f"{username}/{post.date_utc.strftime('%Y-%m-%d')}_{shortcode}.jpg"


async def download_instagram_media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text.strip()
    username = url.split("/")[3]
    try:
        start_msg = await update.message.reply_text("در حال دانلود...")
        photo_path = download_instagram_post(url, username)
        await context.bot.send_photo(
            chat_id=update.message.chat_id, photo=open(photo_path, "rb")
        )
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=start_msg.message_id)
        os.remove(photo_path)
    except Exception as e:
        await update.message.reply_text(f"خطا در دانلود عکس: {e}")


def is_instagram_link(text: str) -> bool:
    return "instagram.com" in text
