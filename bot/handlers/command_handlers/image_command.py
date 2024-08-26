from telegram import Update, InputFile, InputMediaPhoto
from telegram.ext import CallbackContext
import os, time, requests
import tempfile
import logging
from bot.utils.image_generator import generate_image
from bot.utils.general_constants import ALLOWED_GROUP_IDS
from bot.utils.image_generator import models, BANNED_WORDS

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

COOLDOWN_TIME = 30
cooldown_users = {}

async def image_command(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        return
    
    user_id = update.effective_user.id
    args = context.args
    if len(args) < 1:
        await update.message.reply_text(f"لطفاً یک پرامپت وارد کنید.\n"
                                        f"مدل های موجود: {', '.join(models.keys())}"
                                        )
        return

    if (
        user_id not in cooldown_users
        or time.time() - cooldown_users[user_id] > COOLDOWN_TIME
    ):
        cooldown_users[user_id] = time.time()

        # Combine args into a single prompt string
        prompt = " ".join(args)

        # Check for banned words
        if any(banned_word in prompt.lower() for banned_word in BANNED_WORDS):
            await update.message.reply_text("پرامپت شما شامل محتوای نامناسب است. لطفاً دوباره تلاش کنید.")
            return

        # Determine if a model is mentioned in the command
        model_key = next((arg for arg in args if arg in models), None)
        if model_key:
            model = models[model_key]
            # Remove model key from the prompt
            prompt = " ".join(arg for arg in args if arg != model_key)
        else:
            # Use the default model (the first one in the dictionary)
            model = next(iter(models.values()))

        response_message = await update.message.reply_text(
            f"در حال ساختن تصویر با {model_key or 'default model'}..."
        )

        try:
            image_urls = await generate_image(prompt, model)
            logger.debug(f"Generated image URLs: {image_urls}")

            if not image_urls:
                await update.message.reply_text("هیچ تصویری ایجاد نشد. لطفاً دوباره تلاش کنید.")
                return
            
            media_group = []
            temp_files = []  # Keep track of temp files for later cleanup

            for i, url in enumerate(image_urls):
                logger.debug(f"Processing image URL: {url}")
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                        for chunk in response.iter_content(1024):
                            temp_file.write(chunk)
                        temp_file_path = temp_file.name
                        temp_files.append(temp_file_path)
                    
                    logger.debug(f"Temporary file created: {temp_file_path}")
                    
                    media_group.append(
                        InputMediaPhoto(
                            media=InputFile(temp_file_path),
                            caption=f"تصویر {i+1} برای پرامپت:\n '{prompt}'\n\n با مدل {model_key or 'default model'}" if i == 0 else None
                        )
                    )
                else:
                    logger.error(f"Failed to download image: {url}, Status code: {response.status_code}")
                    await update.message.reply_text(f"خطا در دانلود تصویر... {url}")

            logger.debug(f"Media group prepared: {media_group}")

            if media_group:
                await context.bot.send_media_group(
                    chat_id=update.effective_chat.id,
                    media=media_group
                )
                logger.info("Media group sent successfully")

                # Clean up the temporary files
                for temp_file_path in temp_files:
                    os.remove(temp_file_path)
                    logger.debug(f"Temporary file removed: {temp_file_path}")
            else:
                logger.warning("No media to send")

        except Exception as e:
            logger.exception(f"Error in image_command: {e}")
            await update.message.reply_text(
                f"خطایی رخ داده است: {str(e)}"
            )

        await response_message.delete()
        
    else:
        remaining_time = COOLDOWN_TIME - (time.time() - cooldown_users[user_id])
        await update.message.reply_text(
            f"لطفاً {remaining_time:.0f} ثانیه صبر کنید.\n\n"f"هر 30 ثانیه مجدداً تلاش کنید."
        )
