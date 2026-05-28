import logging
import asyncio
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from app.config import LOG_LEVEL, TELEGRAM_BOT_TOKEN
from app.database import init_db
from app.handlers import control, query, start, vps_manage
from app.utils import admin_only

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO)
)
logger = logging.getLogger(__name__)

@admin_only
async def route_text_message(update, context):
    text = update.message.text
    if text == "📊 VPS 列表":
        await vps_manage.list_vps(update, context)
    elif text == "📈 查询流量":
        await query.query_traffic_menu(update, context)
    elif text == "🌐 查询全部":
        await query.query_all(update, context)
    elif text == "⚙️ 控制 VPS":
        await control.control_menu(update, context)

def main():
    """Start the bot."""
    asyncio.run(init_db())

    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is missing. Please check your .env file.")
        return

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start.start_cmd))

    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^➕ 添加 VPS$"), vps_manage.add_vps_start),
            CallbackQueryHandler(vps_manage.add_vps_start, pattern="^add_vps_start$"),
        ],
        states={
            vps_manage.NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, vps_manage.add_vps_name)],
            vps_manage.VEID: [MessageHandler(filters.TEXT & ~filters.COMMAND, vps_manage.add_vps_veid)],
            vps_manage.API_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, vps_manage.add_vps_apikey)],
            vps_manage.SSH_PORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, vps_manage.add_vps_ssh_port)],
            vps_manage.NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, vps_manage.add_vps_note)],
            vps_manage.EXPIRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, vps_manage.add_vps_expiry)],
        },
        fallbacks=[CommandHandler("cancel", vps_manage.cancel)],
    )
    application.add_handler(conv_handler)

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route_text_message))
    application.add_handler(CallbackQueryHandler(vps_manage.vps_action_callback, pattern="^(del_|list_vps_back)"))
    application.add_handler(CallbackQueryHandler(query.traffic_callback, pattern="^traffic_"))
    application.add_handler(CallbackQueryHandler(control.control_callback, pattern="^(ctrl_|action_|execute_)"))

    logger.info("BWG VPS Telegram Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
