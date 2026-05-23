import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # Parse admin IDs from comma-separated string to a set of integers
    _admin_ids_str = os.getenv("ADMIN_USER_IDS", "")
    ADMIN_USER_IDS = set()
    for admin_id in _admin_ids_str.split(","):
        admin_id = admin_id.strip()
        if admin_id.isdigit():
            ADMIN_USER_IDS.add(int(admin_id))
            
    DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/bot.db")
    TIMEZONE = os.getenv("TIMEZONE", "Asia/Shanghai")
    KIWIVM_API_BASE = os.getenv("KIWIVM_API_BASE", "https://api.64clouds.com/v1")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "20"))
