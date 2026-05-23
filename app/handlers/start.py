from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, Application
from app.utils import admin_required

@admin_required
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message with the main menu."""
    keyboard = [
        [KeyboardButton("📊 VPS 列表"), KeyboardButton("➕ 添加 VPS")],
        [KeyboardButton("📈 查询流量"), KeyboardButton("🌐 查询全部")],
        [KeyboardButton("⚙️ 控制 VPS"), KeyboardButton("ℹ️ 帮助")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "欢迎使用 BWG VPS 管理机器人，请选择功能：",
        reply_markup=reply_markup
    )

@admin_required
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help information."""
    await update.message.reply_text(
        "BWG VPS 管理机器人使用说明：\n\n"
        "1. 使用菜单栏按钮进行操作。\n"
        "2. 需在添加 VPS 时输入正确的 VEID 和 API_KEY。\n"
        "3. 管理员权限请在配置文件中设置。"
    )

def setup_start_handlers(application: Application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("^ℹ️ 帮助$"), help_command))
