from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from app.repositories.vps_repository import VpsRepository
from app.services.formatter import format_bytes, format_timestamp
from app.services.kiwivm_client import KiwiVMClient
from app.utils import admin_only


async def show_traffic_list(obj):
    vps_list = await VpsRepository.get_all_vps()
    if not vps_list:
        text = "📂 没有找到 VPS，请先添加。"
        if hasattr(obj, "edit_message_text"):
            await obj.edit_message_text(text)
        else:
            await obj.reply_text(text)
        return

    keyboard = [[InlineKeyboardButton(vps["name"], callback_data=f"traffic_{vps['id']}")] for vps in vps_list]
    text = "请选择要查询详细信息的 VPS："
    if hasattr(obj, "edit_message_text"):
        await obj.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await obj.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


@admin_only
async def query_traffic_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_traffic_list(update.message)


@admin_only
async def traffic_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "traffic_back":
        await show_traffic_list(query)
        return

    if not data.startswith("traffic_"):
        return

    vps_id = int(data.split("_")[1])
    vps = await VpsRepository.get_vps(vps_id)
    if not vps:
        back = [[InlineKeyboardButton("🔙 返回", callback_data="traffic_back")]]
        await query.edit_message_text("❌ VPS 不存在。", reply_markup=InlineKeyboardMarkup(back))
        return

    await query.edit_message_text("⏳ 正在向 KiwiVM API 获取数据...")
    client = KiwiVMClient(vps["veid"], vps["api_key"])
    info = await client.get_service_info()
    back_btn = [[InlineKeyboardButton("🔙 返回上一层", callback_data="traffic_back")]]

    if info.get("error") != 0:
        await query.edit_message_text(f"❌ 查询失败：{info.get('message')}", reply_markup=InlineKeyboardMarkup(back_btn))
        return

    multiplier = info.get("monthly_data_multiplier", 1)
    plan_data = info.get("plan_monthly_data", 0) * multiplier
    used_data = info.get("data_counter", 0) * multiplier
    remain_data = plan_data - used_data if plan_data > used_data else 0
    usage_pct = (used_data / plan_data * 100) if plan_data > 0 else 0
    status = "🟠 Suspended" if info.get("suspended") else "🟢 Active"
    ip = info.get("ip_addresses", ["N/A"])[0]
    ssh_port = vps.get("ssh_port") or "22"

    text = (
        f"VPS：<b>{vps['name']}</b>\n"
        f"主机名：<code>{info.get('hostname', 'N/A')}</code>\n"
        f"IP：<code>{ip}</code>\n"
        f"SSH端口：<code>{ssh_port}</code>\n"
        f"机房：<code>{info.get('node_location', 'N/A')}</code>\n"
        f"系统：<code>{info.get('os', 'N/A')}</code>\n\n"
        f"📊 <b>本月流量</b>：\n"
        f"已用：{format_bytes(used_data)}\n"
        f"总量：{format_bytes(plan_data)}\n"
        f"剩余：{format_bytes(remain_data)}\n"
        f"使用率：{usage_pct:.2f}%\n\n"
        f"💾 <b>硬件配额</b>：\n"
        f"RAM: {format_bytes(info.get('plan_ram', 0))} | "
        f"Swap: {format_bytes(info.get('plan_swap', 0))} | "
        f"Disk: {format_bytes(info.get('plan_disk', 0))}\n\n"
        f"🔄 <b>下次流量重置</b>：\n<code>{format_timestamp(info.get('data_next_reset'))}</code>\n\n"
        f"📅 到期时间：{vps['expiry_date'] or '未设置'}\n"
        f"🚥 状态：{status}"
    )
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(back_btn), parse_mode="HTML")


@admin_only
async def query_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⏳ 正在查询所有 VPS 信息，请稍候...")
    vps_list = await VpsRepository.get_all_vps()
    if not vps_list:
        await msg.edit_text("📂 没有找到 VPS。")
        return

    results = []
    failed = []
    for vps in vps_list:
        client = KiwiVMClient(vps["veid"], vps["api_key"])
        info = await client.get_service_info()
        if info.get("error") == 0:
            multiplier = info.get("monthly_data_multiplier", 1)
            plan_data = info.get("plan_monthly_data", 0) * multiplier
            used_data = info.get("data_counter", 0) * multiplier
            usage = (used_data / plan_data * 100) if plan_data > 0 else 0
            ip = info.get("ip_addresses", [""])[0]
            reset_time = format_timestamp(info.get("data_next_reset"))
            status = "🟠 Suspended" if info.get("suspended") else "🟢 Active"
            note = vps.get("note") or ""
            ssh_port = vps.get("ssh_port") or "22"
            note_display = f"\n   📝 备注：<code>{note}</code>" if note else ""
            results.append(
                f"▪️ <b>{vps['name']}</b> (<code>{ip}:{ssh_port}</code>)\n"
                f"   {status} | 流量: {format_bytes(used_data)} / {format_bytes(plan_data)} ({usage:.1f}%){note_display}\n"
                f"   🔄 重置：<code>{reset_time}</code>\n"
                f"   💾 配额：RAM {format_bytes(info.get('plan_ram', 0))} | Disk {format_bytes(info.get('plan_disk', 0))}"
            )
        else:
            failed.append(f"{vps['name']}: {info.get('message')}")

    final_text = "🌐 <b>全部 VPS 概况</b>\n\n" + "\n\n".join(results)
    if failed:
        final_text += "\n\n❌ <b>失败列表</b>：\n" + "\n".join(failed)

    await msg.edit_text(final_text, parse_mode="HTML")
