from telegram import Update
from telegram.ext import CallbackContext
from bot.utils.general_constants import ALLOWED_GROUP_IDS
import os
import logging
import re
import subprocess
from pydub import AudioSegment
from telegram import InputFile
from bot.utils.audio_demo_creator import last_demo_messages

DOWNLOAD_PATH = "downloads"
MAX_VOICE_SIZE = 50 * 1024 * 1024

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename).replace(' ', '_')

def create_audio_demo_from(file_path, start_time, duration):
    try:
        audio = AudioSegment.from_file(file_path)
    except:
        temp_wav = file_path + ".wav"
        try:
            subprocess.run(["ffmpeg", "-i", file_path, temp_wav], check=True, capture_output=True)
            audio = AudioSegment.from_wav(temp_wav)
        finally:
            if os.path.exists(temp_wav):
                os.remove(temp_wav)

    start_ms = start_time * 1000
    duration_ms = duration * 1000
    demo_audio = audio[start_ms:start_ms + duration_ms]
    demo_path = file_path.rsplit('.', 1)[0] + f"_demo_{start_time}s.ogg"
    demo_audio.export(demo_path, format="ogg")
    demo_size = os.path.getsize(demo_path)
    return demo_path, demo_size

class ProgressUploader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_size = os.path.getsize(file_path)

    async def upload(self, bot, chat_id, caption=None, as_voice=False):
        with open(self.file_path, 'rb') as file:
            input_file = InputFile(file)
            if as_voice:
                return await bot.send_voice(
                    chat_id=chat_id,
                    voice=input_file,
                    caption=caption,
                    read_timeout=300,
                    write_timeout=300
                )
            else:
                return await bot.send_document(
                    chat_id=chat_id,
                    document=input_file,
                    caption=caption,
                    read_timeout=300,
                    write_timeout=300
                )

async def from_command(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        await update.message.reply_text("این گروه، گروه تایپولوژی نیست.")
        return
    
    if not update.message.reply_to_message or not update.message.reply_to_message.audio:
        await update.message.reply_text("لطفاً این دستور را با ریپلای به یک فایل صوتی ارسال کنید. مثال:\n /from 10")
        return

    try:
        start_time = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text("لطفاً یک عدد صحیح برای زمان شروع وارد کنید. مثال:\n /from 10")
        return

    audio = update.message.reply_to_message.audio
    duration = audio.duration

    if start_time >= duration:
        await update.message.reply_text(f"زمان شروع نمی‌تواند بیشتر از مدت زمان فایل ({duration}s) باشد.")
        return

    file_id = audio.file_id
    file_name = audio.file_name or f"audio_{file_id}.mp3"
    file_name = sanitize_filename(file_name)
    title = audio.title or audio.performer or os.path.splitext(file_name)[0]

    file_path = os.path.join(DOWNLOAD_PATH, file_name)
    demo_path = None

    try:
        file = await context.bot.get_file(file_id)
        await file.download_to_drive(custom_path=file_path)

        loading_message = await update.message.reply_text("در حال ایجاد فایل صوتی...")
        demo_duration = min(30, duration - start_time)
        demo_path, demo_size = create_audio_demo_from(file_path, start_time, demo_duration)

        if update.effective_user.id in last_demo_messages:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=last_demo_messages[update.effective_user.id]
                )
            except Exception as e:
                logging.error(f"Error deleting previous demo: {e}")

        uploader = ProgressUploader(demo_path)
        demo_message = await uploader.upload(
            context.bot,
            update.message.chat_id,
            caption=f"دموی {title} (from {start_time}s)",
            as_voice=True if demo_size <= MAX_VOICE_SIZE else False
        )
        
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=loading_message.message_id)

        last_demo_messages[update.effective_user.id] = demo_message.message_id

    except Exception as e:
        logging.error(f"Error in from_command: {e}")
        await update.message.reply_text("متأسفانه در پردازش فایل صوتی خطایی رخ داد. لطفاً دوباره تلاش کنید.")
        return

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        if demo_path and os.path.exists(demo_path):
            os.remove(demo_path)