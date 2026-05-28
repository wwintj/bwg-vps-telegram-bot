import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler
from app.repositories.vps_repository import VpsRepository
from app.services.kiwivm_client import KiwiVMClient
from app.utils import admin_only

NAME, VEID, API_KEY, SSH_PORT, NOTE, EXPIRY = range(6)


@admin_only
async def add_vps_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "➕ 请输入自定义的 VPS 名称，例如 HK-01。\n输入 /cancel 取消操作。"

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(text)
    else:
        await update.message.reply_text(text)

    return NAME


async def add_vps_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("请输入这台 VPS 的 VEID：")
    return VEID


async def add_vps_veid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["veid"] = update.message.text.strip()
    await update.message.reply_text("请输入这台 VPS 的 API_KEY：")
    return API_KEY


async def add_vps_apikey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["api_key"] = update.message.text.strip()
    await update.message.reply_text("请输入该 VPS 的 SSH 端口号，默认通常是 22：")
    return SSH_PORT


async def add_vps_ssh_port(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ssh_port"] = update.message.text.strip()
    await update.message.reply_text("请输入备注信息，如果不填请输入 skip：")
    return NOTE


async def add_vps_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    note = update.message.text.strip()
    context.user_data["note"] = "" if note.lower() == "skip" else note
    await update.message.reply_text("请输入到期时间，例如 2026-12-31；如果不填请输入 skip：")
    return EXPIRY


async def add_vps_expiry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    expiry = update.message.text.strip()
    context.user_data["expiry"] = "" if expiry.lower() == "skip" else expiry

    msg = await update.message.reply_text("⏳ 正在验证 API 有效性...")
    veid = context.user_data["veid"]
    api_key = context.user_data["api_key"]
    client = KiwiVMClient(veid, api_key)
    info = await client.get_service_info()

    if info.get("error") == 0:
        await VpsRepository.add_vps(
            name=context.user_data["name"],
            veid=veid,
            api_key=api_key,
            ssh_port=context.user_data["ssh_port"],
            note=context.user_data["note"],
            expiry_date=context.user_data["expiry"],
        )
        await msg.edit_text(f"✅ 添加成功！获取到主机名: `{info.get('hostname')}`", parse_mode="Markdown")
    else:
        await msg.edit_text(f"❌ API 验证失败: {info.get('message', '未知错误')}\n请检查 VEID 和 API_KEY 是否正确。")

    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("已取消操作。")
    context.user_data.clear()
    return ConversationHandler.END


@admin_only
async def list_vps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    vps_list = await VpsRepository.get_all_vps()

    if not vps_list:
        text = "📂 当前没有保存任何 VPS。请点击下方按钮添加。"
        keyboard = [[InlineKeyboardButton("➕ 添加 VPS", callback_data="add_vps_start")]]

        if update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    loading_text = "⏳ 正在并发获取 IP 并探测网络状态，请稍候..."
    if update.callback_query:
        msg = await update.callback_query.edit_message_text(loading_text)
    else:
        msg = await update.message.reply_text(loading_text)

    async def fetch_ip_and_status(vps):
        client = KiwiVMClient(vps["veid"], vps["api_key"])
        info = await client.get_service_info()
        ip = "获取失败"
        status = "❌ API错误"

        if info.get("error") == 0:
            ip = info.get("ip_addresses", ["获取失败"])[0]
            if info.get("suspended"):
                status = "🟠 Suspended"
            elif ip == "获取失败":
                status = "🔴 Error"
            else:
                try:
                    port = int(vps.get("ssh_port") or 22)
                    reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=1.5)
                    writer.close()
                    await writer.wait_closed()
                    status = "🟢 Running"
                except Exception:
                    status = "🔴 Stopped"

        return vps, ip, status

    results = await asyncio.gather(*(fetch_ip_and_status(vps) for vps in vps_list))

    text = "📊 **现有 VPS 列表**\n\n"
    for vps, ip, status in results:
        note = vps.get("note") or "无"
        ssh_port = vps.get("ssh_port") or "22"
        expiry = vps["expiry_date"] or "未知"
        text += f"🖥️ 名称: **{vps['name']}** (IP: `{ip}`)\n"
        text += f"📅 到期: {expiry} | SSH端口: {ssh_port}\n"
        text += f"🚥 状态: {status} | 备注: {note}\n\n"

    keyboard = [[
        InlineKeyboardButton("➕ 添加 VPS", callback_data="add_vps_start"),
        InlineKeyboardButton("🗑️ 删除 VPS", callback_data="del_menu"),
    ]]

    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    else:
        await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


@admin_only
async def vps_action_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "del_menu":
        vps_list = await VpsRepository.get_all_vps()
        if not vps_list:
            keyboard = [[InlineKeyboardButton("🔙 返回上一层", callback_data="list_vps_back")]]
            await query.edit_message_text("📂 没有可删除的 VPS。", reply_markup=InlineKeyboardMarkup(keyboard))
            return

        keyboard = [[InlineKeyboardButton(f"❌ 删除 {vps['name']}", callback_data=f"del_confirm_{vps['id']}")] for vps in vps_list]
        keyboard.append([InlineKeyboardButton("🔙 返回上一层", callback_data="list_vps_back")])
        await query.edit_message_text("⚠️ 请选择要删除的 VPS：", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "list_vps_back":
        await list_vps(update, context)
    elif data.startswith("del_confirm_"):
        vps_id = data.split("_")[2]
        keyboard = [[
            InlineKeyboardButton("⚠️ 确认删除", callback_data=f"del_do_{vps_id}"),
            InlineKeyboardButton("🔙 取消返回", callback_data="list_vps_back"),
        ]]
        await query.edit_message_text("⚠️ 确定要删除该 VPS 记录吗？这不会影响服务器本身。", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data.startswith("del_do_"):
        vps_id = int(data.split("_")[2])
        await VpsRepository.delete_vps(vps_id)
        await list_vps(update, context)
