import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_USER_IDS = {
    int(admin_id.strip())
    for admin_id in os.getenv("ADMIN_USER_IDS", "").split(",")
    if admin_id.strip().isdigit()
}
DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/bot.db")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Shanghai")
KIWIVM_API_BASE = os.getenv("KIWIVM_API_BASE", "https://api.64clouds.com/v1")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "20"))
