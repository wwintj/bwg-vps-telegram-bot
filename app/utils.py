import logging
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from app.config import ADMIN_USER_IDS

logger = logging.getLogger(__name__)

def admin_only(func):
    """Decorator to restrict handler access to admin users only."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not update.effective_user:
            return

        user_id = update.effective_user.id
        if user_id not in ADMIN_USER_IDS:
            logger.warning(f"Unauthorized access attempt by user ID: {user_id}")
            error_msg = "⛔️ 你没有权限使用这个机器人。"

            if update.message:
                await update.message.reply_text(error_msg)
            elif update.callback_query:
                await update.callback_query.answer(error_msg, show_alert=True)
            return

        return await func(update, context, *args, **kwargs)
    return wrapper

admin_required = admin_only
