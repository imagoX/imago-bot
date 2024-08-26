from telegram import Update
from telegram.ext import filters
from telegram.ext import ContextTypes
from bot.utils.general_constants import ALLOWED_GROUP_IDS

class MessageFilter(filters.UpdateFilter):
    def __init__(self, startup_time):
        super().__init__()
        self.startup_time = startup_time

    def filter(self, update: Update) -> bool:
        if update.message:
            return update.message.date > self.startup_time
        return False

class CustomFilters:
    class SpecificGroupFilter(filters.BaseFilter):
        def filter(self, message):
            print(message.chat.id)
            return message.chat.id in ALLOWED_GROUP_IDS

    specific_group = SpecificGroupFilter()