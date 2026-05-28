import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from app.repositories.vps_repository import VpsRepository
from app.services.kiwivm_client import KiwiVMClient
from app.utils import admin_only


async def check_tcp_port(ip: str, port: int) -> bool:
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=2.0)
        writer.close()
        await writer.wait_closed()
        return True
    except Exception:
        return False


async def show_control_list(obj):
    vps_list = await VpsRepository.get_all_vps()
    if not vps_list:
        text = "📂 没有找到 VPS，请先添加。"
        if hasattr(obj, "edit_message_text"):
            await obj.edit_message_text(text)
        else:
            await obj.reply_text(text)
        return

    keyboard = [[InlineKeyboardButton(vps["name"], callback_data=f"ctrl_{vps['id']}")] for vps in vps_list]
    text = "请选择要控制的 VPS："
    if hasattr(obj, "edit_message_text"):
        await obj.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await obj.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


@admin_only
async def control_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_control_list(update.message)


@admin_only
async def control_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "ctrl_back":
        await show_control_list(query)
    elif data.startswith("ctrl_"):
        vps_id = data.split("_")[1]
        keyboard = [
            [
                InlineKeyboardButton("🟢 开机 (Start)", callback_data=f"action_start_{vps_id}"),
                InlineKeyboardButton("🔴 关机 (Stop)", callback_data=f"action_stop_{vps_id}"),
            ],
            [
                InlineKeyboardButton("🔄 重启 (Restart)", callback_data=f"action_restart_{vps_id}"),
                InlineKeyboardButton("⚠️ 强关 (Kill)", callback_data=f"action_kill_{vps_id}"),
            ],
            [InlineKeyboardButton("✈️ 迁移机房 (Migrate)", callback_data=f"action_migrate_{vps_id}")],
            [InlineKeyboardButton("🔙 返回上一层", callback_data="ctrl_back")],
        ]
        await query.edit_message_text("⚙️ 请选择操作：", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data.startswith("action_"):
        parts = data.split("_", 3)
        action = parts[1]
        vps_id = parts[2]

        if action == "migrate":
            await query.edit_message_text("⏳ 正在获取当前可用机房列表...")
            vps = await VpsRepository.get_vps(int(vps_id))
            client = KiwiVMClient(vps["veid"], vps["api_key"])
            res = await client._request("migrate/getLocations")

            if res.get("error") == 0:
                current = res.get("currentLocation", "未知")
                locations = res.get("locations", [])
                descriptions = res.get("descriptions", {})
                if not locations:
                    keyboard = [[InlineKeyboardButton("🔙 返回控制菜单", callback_data=f"ctrl_{vps_id}")]]
                    await query.edit_message_text("❌ 当前没有可迁移的机房。", reply_markup=InlineKeyboardMarkup(keyboard))
                    return

                keyboard = [
                    [InlineKeyboardButton(descriptions.get(location, location), callback_data=f"action_migconf_{vps_id}_{location}")]
                    for location in locations
                ]
                keyboard.append([InlineKeyboardButton("🔙 取消返回", callback_data=f"ctrl_{vps_id}")])
                text = f"✈️ **机房迁移 (Migrate)**\n当前机房：`{current}`\n\n请选择目标机房："
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            else:
                keyboard = [[InlineKeyboardButton("🔙 返回控制菜单", callback_data=f"ctrl_{vps_id}")]]
                await query.edit_message_text(f"❌ 获取机房失败: {res.get('message')}", reply_markup=InlineKeyboardMarkup(keyboard))
        elif action == "migconf":
            location = parts[3]
            text = (
                f"⚠️ **高危操作确认**\n\n"
                f"确定要将机房迁移到 `{location}` 吗？\n\n"
                f"1. 迁移将导致 IP 地址发生永久变化。\n"
                f"2. 迁移过程中 VPS 将关机，并在后台进行数据拷贝。\n"
                f"3. 请确保没有正在运行的重要数据写入任务。"
            )
            keyboard = [
                [InlineKeyboardButton("✅ 确认开始迁移", callback_data=f"execute_migrate_{vps_id}_{location}")],
                [InlineKeyboardButton("🔙 取消返回", callback_data=f"action_migrate_{vps_id}")],
            ]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        else:
            warning = "\n‼️ **警告：强制关机可能导致未保存的数据丢失或文件系统损坏！**" if action == "kill" else ""
            keyboard = [[
                InlineKeyboardButton("✅ 确认执行", callback_data=f"execute_{action}_{vps_id}"),
                InlineKeyboardButton("🔙 取消返回", callback_data=f"ctrl_{vps_id}"),
            ]]
            await query.edit_message_text(f"确定要执行 `{action.upper()}` 操作吗？{warning}", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data.startswith("execute_"):
        parts = data.split("_", 3)
        action = parts[1]
        vps_id = parts[2]
        vps = await VpsRepository.get_vps(int(vps_id))
        client = KiwiVMClient(vps["veid"], vps["api_key"])
        back_btn = [[InlineKeyboardButton("🔙 返回控制菜单", callback_data=f"ctrl_{vps_id}")]]

        if action == "migrate":
            location = parts[3]
            await query.edit_message_text(f"⏳ 正在提交机房迁移请求 ({location})...")
            res = await client._request("migrate/start", location=location)
            if res.get("error") == 0:
                await query.edit_message_text("✅ **迁移请求已成功提交！**\n\n请稍后查看新 IP 状态。", reply_markup=InlineKeyboardMarkup(back_btn), parse_mode="Markdown")
            else:
                await query.edit_message_text(f"❌ 迁移失败: {res.get('message')}", reply_markup=InlineKeyboardMarkup(back_btn))
            return

        await query.edit_message_text("⏳ 正在发送控制命令，并获取网络探测信息...")
        info = await client.get_service_info()
        ip = info.get("ip_addresses", [""])[0]
        try:
            ssh_port = int(vps.get("ssh_port", 22))
        except (ValueError, TypeError):
            ssh_port = 22

        res = await client.execute_action(action)
        if res.get("error") != 0:
            await query.edit_message_text(f"❌ 控制失败: {res.get('message')}", reply_markup=InlineKeyboardMarkup(back_btn))
            return

        status_msg = ""
        if ip:
            if action in ["stop", "kill"]:
                await query.edit_message_text(f"⏳ `{action}` 命令已送达，正在探测 SSH 端口确认关机...")
                for _ in range(5):
                    await asyncio.sleep(2)
                    if not await check_tcp_port(ip, ssh_port):
                        status_msg = "\n\n📡 **探测反馈**：SSH 端口已离线，确认关机成功。"
                        break
                else:
                    status_msg = "\n\n📡 **探测反馈**：等待超时，端口仍在响应，请稍后再试。"
            elif action in ["start", "restart"]:
                await query.edit_message_text(f"⏳ `{action}` 命令已送达，正在等待系统启动响应...")
                for _ in range(10):
                    await asyncio.sleep(3)
                    if await check_tcp_port(ip, ssh_port):
                        status_msg = "\n\n📡 **探测反馈**：SSH 端口已恢复正常连通，确认启动成功。"
                        break
                else:
                    status_msg = "\n\n📡 **探测反馈**：机器尚未启动完成或连通超时。"

        await query.edit_message_text(
            f"✅ **{vps['name']}** 的 `{action}` 指令已执行！{status_msg}",
            reply_markup=InlineKeyboardMarkup(back_btn),
            parse_mode="Markdown",
        )
