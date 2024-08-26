from telegram import Update, ChatMemberUpdated
from telegram.ext import CallbackContext, ContextTypes
from bot.utils.youtube_downloader import is_youtube_link
from bot.utils.youtube_downloader import download_youtube_video_handler
from bot.utils.audio_demo_creator import handle_audio_file
from bot.utils.instagram_downloader import is_instagram_link
from bot.utils.instagram_downloader import download_instagram_media_handler
from bot.utils.general_constants import ALLOWED_GROUP_IDS

async def greet_new_member(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        return
    if update.message.new_chat_members:
        for member in update.message.new_chat_members:
            if member.id != context.bot.id:
                await update.message.reply_text(
                    f"درود {member.full_name} به گروه {update.message.chat.title} خوش آمدید."
                )

async def say_goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        return
    if update.message and update.message.left_chat_member:
        left_member = update.message.left_chat_member
        await update.message.reply_text(
            f"بدرود {left_member.full_name}."
        )


async def handle_message(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        return
    if update.message.text:
        text = update.message.text
        if is_youtube_link(text):
            await download_youtube_video_handler(update, context)
        if is_instagram_link(text):
            await download_instagram_media_handler(update, context)
    elif update.message.audio or (update.message.document and update.message.document.mime_type == 'audio/mpeg'):
        await handle_audio_file(update, context)