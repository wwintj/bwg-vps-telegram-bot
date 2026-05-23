import logging
import asyncio
from telegram.ext import ApplicationBuilder

from app.config import Config
from app.database import init_db
from app.handlers.start import setup_start_handlers
from app.handlers.vps_manage import setup_manage_handlers
from app.handlers.query import setup_query_handlers
from app.handlers.control import setup_control_handlers

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
)
logger = logging.getLogger(__name__)

def main():
    """Start the bot."""
    # Initialize the SQLite database
    asyncio.run(init_db())

    if not Config.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is missing. Please check your .env file.")
        return

    # Create the Application
    application = ApplicationBuilder().token(Config.TELEGRAM_BOT_TOKEN).build()

    # Register handlers from respective modules
    setup_start_handlers(application)
    setup_manage_handlers(application)
    setup_query_handlers(application)
    setup_control_handlers(application)

    # Start the bot
    logger.info("BWG VPS Telegram Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
