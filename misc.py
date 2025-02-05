import os
from config import BOT_TOKEN, adminId, groupId, groupId2, testGroupId

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN", BOT_TOKEN)
# RUNWARE_API = os.getenv("RUNWARE_API_KEY", RUNWARE_API_KEY)
ADMIN_ID = os.getenv("adminId", adminId)
GROUP_ID = os.getenv("groupId", groupId)
GROUP_ID2 = os.getenv("groupId2", groupId2)
TEST_GROUP_ID = os.getenv("testGroupId", testGroupId)

ALLOWED_GROUP_IDS = [GROUP_ID, TEST_GROUP_ID]