#!/usr/bin/env bash

# ====================================================
# BWG VPS Telegram Bot - 卸载脚本
# GitHub: https://github.com/wwintj/bwg-vps-telegram-bot
# ====================================================

# 开启报错即退出模式
set -e

# ==================== 变量定义 ====================
PROJECT_NAME="bwg-vps-telegram-bot"
INSTALL_DIR="/opt/bwg-vps-telegram-bot"
SERVICE_NAME="bwg-vps-telegram-bot"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# ==================== 颜色定义 ====================
RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;36m'
RESET='\033[0m'

echo -e "${BLUE}====================================================${RESET}"
echo -e "${BLUE}       BWG VPS Telegram Bot 卸载与清理向导         ${RESET}"
echo -e "${BLUE}====================================================${RESET}"

# ==================== 1. Root 权限检查 ====================
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}错误：请使用 root 权限运行此脚本！${RESET}"
    echo -e "${YELLOW}请尝试使用: sudo bash uninstall.sh${RESET}"
    exit 1
fi

# ==================== 2. 交互式选择卸载模式 ====================
echo -e "请选择卸载模式："
echo -e "  ${GREEN}1) 普通卸载：仅删除后台服务，保留项目文件、.env配置和数据库 (推荐)${RESET}"
echo -e "  ${RED}2) 完全卸载：删除后台服务并清除所有代码、.env和数据库 (数据不可恢复)${RESET}"
echo -e "  ${YELLOW}3) 取消并退出${RESET}"
read -p "请输入序号 [1-3]: " mode_choice

case $mode_choice in
    1)
        PURGE_DATA=0
        echo -e "${GREEN}已选择：普通卸载模式。${RESET}"
        ;;
    2)
        PURGE_DATA=1
        echo -e "${RED}警告：已选择完全卸载模式！所有用户配置及关联的数据库将被彻底删除！${RESET}"
        ;;
    3)
        echo -e "${YELLOW}已取消卸载操作。${RESET}"
        exit 0
        ;;
    *)
        echo -e "${RED}无效输入，操作已终止。${RESET}"
        exit 1
        ;;
esac

# ==================== 3. 完全卸载二次确认 ====================
if [ "$PURGE_DATA" -eq 1 ]; then
    echo -e ""
    echo -e "${RED}====================================================${RESET}"
    echo -e "${RED}⚠️  高危操作确认  ⚠️${RESET}"
    echo -e "${RED}即将删除目录: $INSTALL_DIR 及其下的所有内容！${RESET}"
    echo -e "${RED}执行此操作将永久丢失该项目在本地保存的所有数据库和配置。${RESET}"
    echo -e "${RED}====================================================${RESET}"
    read -p "请输入大写 DELETE 确认执行完全卸载: " confirm_text
    
    if [ "$confirm_text" != "DELETE" ]; then
        echo -e "${YELLOW}输入不匹配，已取消完全卸载操作。${RESET}"
        exit 1
    fi
    echo -e "${RED}验证通过，开始执行清理流程...${RESET}"
fi

# ==================== 4. 停止并清理 Systemd 服务 ====================
echo -e "${GREEN}\n[1/3] 正在停止并清理后台服务...${RESET}"

# 无条件执行停止与禁用，即使服务不存在也不会报错中断
systemctl stop "$SERVICE_NAME" 2>/dev/null || true
systemctl disable "$SERVICE_NAME" 2>/dev/null || true

if [ -f "$SERVICE_FILE" ]; then
    echo -e "${YELLOW}正在移除 Systemd 服务文件...${RESET}"
    rm -f "$SERVICE_FILE"
    echo -e "${YELLOW}正在重新加载 Systemd 配置并清除残留状态...${RESET}"
    systemctl daemon-reload
    systemctl reset-failed 2>/dev/null || true
    echo -e "${GREEN}Systemd 服务文件已移除。${RESET}"
else
    echo -e "${YELLOW}提示: 服务配置文件 $SERVICE_FILE 不存在，跳过删除。${RESET}"
fi

# ==================== 5. 处理项目文件目录 ====================
echo -e "${GREEN}\n[2/3] 正在处理项目目录...${RESET}"

if [ -d "$INSTALL_DIR" ]; then
    if [ "$PURGE_DATA" -eq 1 ]; then
        echo -e "${RED}正在删除项目目录及所有数据: $INSTALL_DIR ...${RESET}"
        rm -rf "$INSTALL_DIR"
        echo -e "${GREEN}项目目录及数据已删除。${RESET}"
    else
        echo -e "${YELLOW}当前为普通卸载模式，已保留项目目录: $INSTALL_DIR${RESET}"
        echo -e "${GREEN}相关配置与数据库未受影响。${RESET}"
    fi
else
    echo -e "${YELLOW}提示: 未检测到安装目录 $INSTALL_DIR，跳过清理。${RESET}"
fi

# ==================== 6. 报告卸载结果 ====================
echo -e "${GREEN}\n[3/3] 生成卸载报告...${RESET}"
echo -e "${BLUE}====================================================${RESET}"
echo -e "${GREEN}卸载流程执行完毕！${RESET}"
echo -e ""

if [ "$PURGE_DATA" -eq 1 ]; then
    echo -e "${RED}🗑️ 完全卸载报告：${RESET}"
    echo -e "  • 后台服务与配置文件已被彻底移除。"
    echo -e "  • 虚拟环境、本地配置 (.env) 及 SQLite 数据库 (bot.db) 均已删除。"
else
    echo -e "${YELLOW}📦 普通卸载报告：${RESET}"
    echo -e "  • 后台开机自启服务已被移除。"
    echo -e ""
    echo -e "  ${BLUE}保留的文件及配置位置：${RESET}"
    echo -e "  环境变量配置 (.env) : ${GREEN}$INSTALL_DIR/.env${RESET}"
    echo -e "  本地资产数据库 (db)  : ${GREEN}$INSTALL_DIR/data/bot.db${RESET}"
    echo -e ""
    echo -e "  ${YELLOW}💡 重新安装指引：${RESET}"
    echo -e "  若需恢复运行，请重新执行: ${BLUE}sudo bash install.sh${RESET}"
    echo -e "  安装过程中选择 ${GREEN}1) 保留配置和数据库${RESET} 即可继续使用原有环境。"
fi
echo -e "${BLUE}====================================================${RESET}"
