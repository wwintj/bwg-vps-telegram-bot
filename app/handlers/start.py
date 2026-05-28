from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes
from app.utils import admin_only

@admin_only
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message with the main menu."""
    keyboard = [
        ["📊 VPS 列表", "⚙️ 控制 VPS"],
        ["📈 查询流量", "🌐 查询全部"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "👋 欢迎使用 BandwagonHost/KiwiVM 管理机器人！\n请选择下方菜单进行操作：",
        reply_markup=reply_markup
    )
