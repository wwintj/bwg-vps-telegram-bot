#!/usr/bin/env bash

# ====================================================
# BWG VPS Telegram Bot - 平滑升级脚本
# GitHub: https://github.com/wwintj/bwg-vps-telegram-bot
# ====================================================

# 开启报错即退出模式
set -e

# ==================== 变量定义 ====================
PROJECT_NAME="bwg-vps-telegram-bot"
INSTALL_DIR="/opt/bwg-vps-telegram-bot"
SERVICE_NAME="bwg-vps-telegram-bot"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
BACKUP_DIR="${INSTALL_DIR}/backups/update-${TIMESTAMP}"

# ==================== 颜色定义 ====================
RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;36m'
RESET='\033[0m'

echo -e "${BLUE}====================================================${RESET}"
echo -e "${BLUE}       BWG VPS Telegram Bot 平滑升级向导           ${RESET}"
echo -e "${BLUE}====================================================${RESET}"

# ==================== 0. 全局错误捕获机制 ====================
# 如果任何命令执行失败（触发 set -e），该函数将自动接管并输出恢复指引
function on_error() {
    echo -e "\n${RED}❌ 更新过程中发生严重错误，升级已中断！${RESET}"
    if [ -d "$BACKUP_DIR" ]; then
        echo -e "${YELLOW}不用担心，您的核心数据在升级前已被安全备份至：${RESET}"
        echo -e "${GREEN}${BACKUP_DIR}${RESET}"
        echo -e ""
        echo -e "${YELLOW}🛠️  如果需要手动恢复数据，请依次执行以下命令：${RESET}"
        echo -e "  cp -a ${BACKUP_DIR}/.env ${INSTALL_DIR}/.env"
        echo -e "  rm -rf ${INSTALL_DIR}/data"
        echo -e "  cp -a ${BACKUP_DIR}/data ${INSTALL_DIR}/data"
        echo -e "  chmod 700 ${INSTALL_DIR}/data"
        echo -e "  chmod 600 ${INSTALL_DIR}/.env 2>/dev/null || true"
        echo -e "  sudo systemctl restart ${SERVICE_NAME}"
    fi
    echo -e "${BLUE}====================================================${RESET}"
    exit 1
}
trap 'on_error' ERR

# ==================== 1. Root 权限检查 ====================
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}错误：请使用 root 权限运行此脚本！${RESET}"
    echo -e "${YELLOW}请尝试使用: sudo bash update.sh${RESET}"
    exit 1
fi

# ==================== 2. 目录状态与 Git 检查 ====================
echo -e "${GREEN}[1/6] 正在检查项目运行环境...${RESET}"

if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${RED}错误：未找到安装目录 ${INSTALL_DIR} ！${RESET}"
    echo -e "${YELLOW}请先执行初次安装：sudo bash install.sh${RESET}"
    exit 1
fi

if [ ! -d "$INSTALL_DIR/.git" ]; then
    echo -e "${RED}错误：目标目录 ${INSTALL_DIR} 存在，但不是一个合法的 Git 仓库！${RESET}"
    echo -e "${YELLOW}当前目录无法通过 update.sh 进行平滑升级。为保护您的数据，升级已终止。${RESET}"
    echo -e "请使用备份重构目录，或在其他目录重新执行 install.sh。${RESET}"
    exit 1
fi

# 进入项目工作目录
cd "$INSTALL_DIR" || exit 1

# ==================== 3. 执行核心数据自动备份 ====================
echo -e "${GREEN}[2/6] 正在对核心配置和数据库进行安全备份...${RESET}"

mkdir -p "$BACKUP_DIR"
chmod 700 "${INSTALL_DIR}/backups" 2>/dev/null || true

if [ -f ".env" ]; then
    cp -a .env "$BACKUP_DIR/"
    echo -e "${YELLOW}已备份 .env 配置文件。${RESET}"
fi

if [ -d "data" ]; then
    cp -a data "$BACKUP_DIR/"
    echo -e "${YELLOW}已备份 data/ 数据库目录。${RESET}"
fi

echo -e "${GREEN}备份完成，备份路径: ${BACKUP_DIR}${RESET}"

# ==================== 4. 从 GitHub 拉取最新代码 ====================
echo -e "${GREEN}[3/6] 正在从 GitHub 同步最新代码...${RESET}"

# 严格执行 git 拉取，由于我们在 .gitignore 中排除了 .env 和 data，
# git reset --hard 不会影响这些未追踪（untracked）的核心资产文件。
git fetch origin main
git reset --hard origin/main

echo -e "${YELLOW}代码同步完成。${RESET}"

# ==================== 5. 更新 Python 虚拟环境与依赖 ====================
echo -e "${GREEN}[4/6] 正在检查并更新 Python 依赖环境...${RESET}"

if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}未检测到虚拟环境，正在重新创建 .venv ...${RESET}"
    python3 -m venv .venv
fi

# 升级 pip 并安装最新的 requirements
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

echo -e "${YELLOW}Python 依赖更新完成。${RESET}"

# ==================== 6. 重启并检查 Systemd 服务 ====================
echo -e "${GREEN}[5/6] 正在重新加载 Systemd 配置并重启服务...${RESET}"

systemctl daemon-reload
systemctl restart "$SERVICE_NAME"

echo -e "${GREEN}[6/6] 正在获取服务最新运行状态...${RESET}"
echo -e "${BLUE}====================================================${RESET}"

# 禁用退出拦截，避免正常的 grep/status 代码触发陷阱
trap - ERR 

systemctl status "$SERVICE_NAME" --no-pager

echo -e "${BLUE}====================================================${RESET}"
echo -e "${GREEN}🎉 恭喜！BWG VPS Telegram Bot 已成功升级至最新版本！${RESET}"
echo -e ""
echo -e "  • 您的配置 (.env) 和数据库 (bot.db) 完好无损。"
echo -e "  • 机器人已在后台重新启动并加载最新代码。"
echo -e ""
echo -e "${YELLOW}💡 常用运维命令：${RESET}"
echo -e "  查看服务状态 : ${BLUE}sudo systemctl status $SERVICE_NAME --no-pager${RESET}"
echo -e "  实时运行日志 : ${BLUE}sudo journalctl -u $SERVICE_NAME -f${RESET}"
echo -e "${BLUE}====================================================${RESET}"
echo -e "${RED}⚠️ 注意事项：${RESET}"
echo -e "  每次升级都会在项目下创建 backups/ 目录存放本地备份。"
echo -e "  在配置 .gitignore 时，请务必将 backups/ 排除，避免敏感备份文件被推送到 GitHub！"
echo -e "${BLUE}====================================================${RESET}"
