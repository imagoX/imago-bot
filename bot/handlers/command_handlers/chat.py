from telegram import Update
from telegram.ext import CallbackContext
from bot.utils.chatgpt_integration import generate_chat_response
from bot.utils.general_constants import ALLOWED_GROUP_IDS

async def chat(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.id not in ALLOWED_GROUP_IDS:
        await update.message.reply_text("این گروه، گروه تایپولوژی نیست.")
        return

    user_message = " ".join(context.args)
    if not user_message:
        await update.message.reply_text("لطفاً یک پیام برای چت وارد کنید.")
        return

    response = await generate_chat_response(user_message)

    await update.message.reply_text(response)
