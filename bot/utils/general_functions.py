from telegram.ext import CallbackContext
import logging

from bot.utils.general_constants import ALLOWED_GROUP_IDS


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async def is_user_admin(chat_id: int, user_id: int, context: CallbackContext) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except Exception as e:
        logging.error(f"Error checking admin status: {e}")
        return False


def is_allowed_group(chat_id: int) -> bool:
    return chat_id in ALLOWED_GROUP_IDS
