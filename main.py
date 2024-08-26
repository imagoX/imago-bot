from dotenv import load_dotenv
import asyncio
import signal
import sys
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    filters,
)
from datetime import datetime, timezone
from bot.handlers.command_handlers.info_commnads import get_admins, my_info, chat_info
from bot.handlers.command_handlers.report import report
from bot.handlers.command_handlers.mute import mute
from bot.handlers.command_handlers.unmute import unmute
from bot.handlers.command_handlers.chat import chat
from bot.handlers.command_handlers.ban import ban
from bot.handlers.command_handlers.unban import unban
from bot.handlers.command_handlers.delete import delete_message
from bot.handlers.command_handlers.pin import pin_message
from bot.handlers.command_handlers.unpin import unpin_message
from bot.handlers.command_handlers.unpin_all import unpin_all_messages
from bot.handlers.command_handlers.help import help
from bot.handlers.command_handlers.start import start
from bot.handlers.command_handlers.from_command import from_command
from bot.handlers.command_handlers.image_command import image_command

from bot.handlers.message_handlers import greet_new_member, say_goodbye
from misc import TELEGRAM_BOT_TOKEN, ADMIN_ID
from bot.filters.custom_filter import MessageFilter
from bot.filters.custom_filter import CustomFilters
from bot.handlers.message_handlers import handle_message

load_dotenv()

# Set the root logger to ERROR level
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Set specific loggers to ERROR level
logging.getLogger('telegram').setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.ERROR)

class ErrorOnlyFilter(logging.Filter):
    def filter(self, record):
        return record.levelno >= logging.ERROR

logging.getLogger().addFilter(ErrorOnlyFilter())

async def send_startup_message(application: Application) -> None:
    bot = application.bot
    await bot.send_message(chat_id=ADMIN_ID, text="بات Typology Bot اجرا شد!")

async def error_handler(update: Update, context: CallbackContext) -> None:
    logging.error(f"Update {update} caused error: {context.error}", exc_info=context.error)

async def start_application():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    startup_time = datetime.now(timezone.utc)
    message_filter = MessageFilter(startup_time)

    application.add_handler(CommandHandler("start", start, filters=message_filter))
    application.add_handler(CommandHandler("help", help, filters=message_filter))
    application.add_handler(CommandHandler("ban", ban, filters=message_filter))
    application.add_handler(CommandHandler("unban", unban, filters=message_filter))
    combined_filters = filters.ChatType.GROUPS & filters.REPLY & message_filter
    application.add_handler(CommandHandler("mute", mute, filters=combined_filters))
    application.add_handler(CommandHandler("unmute", unmute, filters=message_filter))
    application.add_handler(CommandHandler("del", delete_message, filters=message_filter))
    application.add_handler(CommandHandler("report", report, filters=message_filter))
    application.add_handler(CommandHandler("pin", pin_message, filters=message_filter))
    application.add_handler(CommandHandler("unpin", unpin_message, filters=message_filter))
    application.add_handler(CommandHandler("unpin_all", unpin_all_messages, filters=message_filter))
    application.add_handler(CommandHandler("admins", get_admins, filters=message_filter))
    application.add_handler(CommandHandler("me", my_info, filters=message_filter))
    application.add_handler(CommandHandler("chat_info", chat_info, filters=message_filter))
    application.add_handler(CommandHandler("chat", chat, filters=message_filter))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND) & message_filter, handle_message))
    application.add_handler(MessageHandler(filters.Document.AUDIO | filters.AUDIO, handle_message))
    application.add_handler(CommandHandler("from", from_command))
    application.add_handler(CommandHandler("image", image_command, filters=message_filter))

    application.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS 
            & filters.ChatType.GROUPS
            & message_filter,
            greet_new_member
        )
    )

    application.add_handler(
        MessageHandler(
            filters.StatusUpdate.LEFT_CHAT_MEMBER
            & filters.ChatType.GROUPS
            & message_filter,
            say_goodbye
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT 
            & filters.ChatType.GROUPS 
            & message_filter,
            handle_message
        )
    )

    application.add_error_handler(error_handler)

    await application.initialize()
    await application.start()
    return application

async def stop_application(application):
    await application.stop()
    await application.shutdown()

def signal_handler(signum, frame):
    raise KeyboardInterrupt

async def main():
    application = await start_application()
    logging.info("Application started. Press Ctrl+C to stop.")
    await send_startup_message(application)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    try:
        await application.updater.start_polling()
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logging.info("Received signal to terminate. Stopping application...")
    finally:
        logging.info("Shutting down...")
        await stop_application(application)

if __name__ == "__main__":
    if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Program interrupted")
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}", exc_info=True)