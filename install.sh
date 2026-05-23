#!/usr/bin/env bash

# ====================================================
# BWG VPS Telegram Bot - 一键安装脚本
# GitHub: https://github.com/wwintj/bwg-vps-telegram-bot
# ====================================================

# 开启报错即退出模式，确保任何一步失败都不会继续盲目执行
set -e

# ==================== 变量定义 ====================
PROJECT_NAME="bwg-vps-telegram-bot"
GITHUB_USER="wwintj"
GITHUB_REPO="bwg-vps-telegram-bot"
GITHUB_URL="https://github.com/wwintj/bwg-vps-telegram-bot.git"
INSTALL_DIR="/opt/bwg-vps-telegram-bot"
SERVICE_NAME="bwg-vps-telegram-bot"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")

# ==================== 颜色定义 ====================
RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;36m'
RESET='\033[0m'

echo -e "${BLUE}====================================================${RESET}"
echo -e "${BLUE}    欢迎使用 BWG VPS Telegram Bot 一键安装脚本    ${RESET}"
echo -e "${BLUE}====================================================${RESET}"

# ==================== 1. Root 权限检查 ====================
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}错误：请使用 root 权限运行此脚本！${RESET}"
    echo -e "${YELLOW}请尝试使用: sudo bash install.sh${RESET}"
    exit 1
fi

# ==================== 2. 系统环境检查 ====================
echo -e "${GREEN}[1/8] 检查系统环境...${RESET}"
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [[ "$ID" != "ubuntu" && "$ID" != "debian" ]]; then
        echo -e "${RED}错误：此脚本仅支持 Ubuntu / Debian 系统！当前系统为: $NAME${RESET}"
        exit 1
    fi
    echo -e "${YELLOW}当前系统: $NAME $VERSION_ID${RESET}"
else
    echo -e "${RED}错误：无法识别当前系统，仅支持 Ubuntu / Debian！${RESET}"
    exit 1
fi

# ==================== 3. 安装系统依赖 ====================
echo -e "${GREEN}[2/8] 更新包列表并安装基础系统依赖...${RESET}"
apt-get update -y
apt-get install -y python3 python3-venv python3-pip git curl ca-certificates
echo -e "${YELLOW}依赖安装完成。${RESET}"

# ==================== 4. 准备项目目录 ====================
echo -e "${GREEN}[3/8] 准备项目目录...${RESET}"
RECONFIGURE_ENV=1

# 检查安装目录是否已存在并询问配置处理
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}检测到安装目录 $INSTALL_DIR 已存在。${RESET}"
    echo -e "请选择操作："
    echo -e "  ${GREEN}1) 保留 .env 和 data 数据库，仅更新/重装程序 (推荐)${RESET}"
    echo -e "  ${YELLOW}2) 重新配置 .env (保留数据库)${RESET}"
    echo -e "  ${RED}3) 退出安装${RESET}"
    read -p "请输入序号 [1-3]: " choice
    case $choice in
        1)
            RECONFIGURE_ENV=0
            echo -e "${GREEN}已选择保留现有配置。${RESET}"
            ;;
        2)
            RECONFIGURE_ENV=1
            echo -e "${YELLOW}已选择重新配置 .env。${RESET}"
            ;;
        3)
            echo -e "${RED}已退出安装。${RESET}"
            exit 0
            ;;
        *)
            echo -e "${RED}无效输入，自动退出安装。${RESET}"
            exit 1
            ;;
    esac
fi

# 核心：确保目标目录是一个合法的 Git 仓库，并同步代码
if [ "$PWD" == "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}当前已在目标目录 $INSTALL_DIR ...${RESET}"
    if [ ! -d ".git" ]; then
        echo -e "${RED}错误：当前所在目录不是一个合法的 Git 仓库！${RESET}"
        echo -e "${YELLOW}为了安全重构目录，请 cd 到其他目录 (如 root 家目录) 后再次执行该脚本。${RESET}"
        exit 1
    else
        echo -e "${YELLOW}正在通过 Git 拉取最新代码...${RESET}"
        if ! git fetch origin main; then
            echo -e "${RED}错误：拉取 GitHub 代码失败！请检查网络连接或仓库是否为空。${RESET}"
            exit 1
        fi
        if ! git reset --hard origin/main; then
            echo -e "${RED}错误：重置 Git 仓库失败！${RESET}"
            exit 1
        fi
    fi
else
    if [ ! -d "$INSTALL_DIR" ]; then
        if [ -d ".git" ] && [ -f "app/main.py" ]; then
            echo -e "${YELLOW}检测到本地完整源码仓库，正在同步至 $INSTALL_DIR (保留 Git 更新能力)...${RESET}"
            mkdir -p "$INSTALL_DIR"
            cp -a . "$INSTALL_DIR/"
        else
            echo -e "${YELLOW}正在从 GitHub 克隆项目至 $INSTALL_DIR...${RESET}"
            if ! git clone "$GITHUB_URL" "$INSTALL_DIR"; then
                echo -e "${RED}错误：克隆 GitHub 仓库失败！${RESET}"
                exit 1
            fi
        fi
    else
        # 目录存在，严格判断是否为 Git 仓库
        if [ ! -d "$INSTALL_DIR/.git" ]; then
            echo -e "${YELLOW}警告: $INSTALL_DIR 存在但不是 Git 仓库！正在进行安全重构...${RESET}"
            
            # 停止可能存在的服务
            systemctl stop "$SERVICE_NAME" 2>/dev/null || true
            
            BACKUP_DIR="${INSTALL_DIR}.bak.${TIMESTAMP}"
            echo -e "${YELLOW}将旧目录重命名为备份: ${BACKUP_DIR}${RESET}"
            mv "$INSTALL_DIR" "$BACKUP_DIR"
            
            echo -e "${YELLOW}重新从 GitHub 克隆标准项目结构...${RESET}"
            if ! git clone "$GITHUB_URL" "$INSTALL_DIR"; then
                echo -e "${RED}错误：克隆 GitHub 仓库失败！正在恢复旧目录...${RESET}"
                mv "$BACKUP_DIR" "$INSTALL_DIR"
                exit 1
            fi
            
            echo -e "${YELLOW}恢复旧版配置与数据...${RESET}"
            if [ -f "${BACKUP_DIR}/.env" ]; then
                cp -a "${BACKUP_DIR}/.env" "$INSTALL_DIR/"
                echo -e "${GREEN}已恢复 .env${RESET}"
            fi
            if [ -d "${BACKUP_DIR}/data" ]; then
                cp -a "${BACKUP_DIR}/data" "$INSTALL_DIR/"
                echo -e "${GREEN}已恢复 data/ 目录${RESET}"
            fi
        else
            echo -e "${YELLOW}目标是一个合法的 Git 仓库，正在拉取最新代码...${RESET}"
            cd "$INSTALL_DIR"
            if ! git fetch origin main; then
                echo -e "${RED}错误：拉取 GitHub 代码失败！请检查网络连接或仓库是否为空。${RESET}"
                exit 1
            fi
            if ! git reset --hard origin/main; then
                echo -e "${RED}错误：重置 Git 仓库失败！${RESET}"
                exit 1
            fi
            cd - > /dev/null
        fi
    fi
fi

# 确保进入项目标准工作目录
cd "$INSTALL_DIR" || exit 1

# 创建数据目录并严格限制权限，保护 SQLite
mkdir -p "$INSTALL_DIR/data"
chmod 700 "$INSTALL_DIR/data"

# ==================== 5. 创建 Python 虚拟环境 ====================
echo -e "${GREEN}[4/8] 创建 Python 虚拟环境并安装依赖...${RESET}"
python3 -m venv .venv
"$INSTALL_DIR/.venv/bin/pip" install --upgrade pip
"$INSTALL_DIR/.venv/bin/pip" install -r requirements.txt
echo -e "${YELLOW}Python 依赖安装完成。${RESET}"

# ==================== 6. 配置环境变量 (.env) ====================
echo -e "${GREEN}[5/8] 配置项目环境变量...${RESET}"

if [ "$RECONFIGURE_ENV" -eq 1 ] || [ ! -f "$INSTALL_DIR/.env" ]; then
    echo -e "${BLUE}=== 请输入 Telegram Bot 配置信息 ===${RESET}"
    
    # 无回显输入保护 Token
    read -s -p "请输入 TELEGRAM_BOT_TOKEN (无回显): " bot_token
    echo ""
    if [ -z "$bot_token" ]; then
        echo -e "${RED}错误：Token 不能为空！安装终止。${RESET}"
        exit 1
    fi

    echo -e "${YELLOW}提示: 若有多个管理员，请用英文逗号分隔，如: 12345678,87654321${RESET}"
    read -p "请输入 ADMIN_USER_IDS: " admin_ids
    if [ -z "$admin_ids" ]; then
        echo -e "${RED}错误：管理员 ID 不能为空！安装终止。${RESET}"
        exit 1
    fi

    read -p "请输入 TIMEZONE (默认: Asia/Shanghai，直接回车即可): " timezone
    timezone=${timezone:-Asia/Shanghai}

    cat > "$INSTALL_DIR/.env" << EOF
TELEGRAM_BOT_TOKEN=$bot_token
ADMIN_USER_IDS=$admin_ids
DATABASE_PATH=./data/bot.db
TIMEZONE=$timezone
KIWIVM_API_BASE=https://api.64clouds.com/v1
LOG_LEVEL=INFO
REQUEST_TIMEOUT=20
EOF
    echo -e "${GREEN}.env 配置文件已生成！${RESET}"
else
    echo -e "${YELLOW}跳过 .env 配置，保留现有设置。${RESET}"
fi

# 配置文件权限设为 600，仅 root 可读写
chmod 600 "$INSTALL_DIR/.env"

# ==================== 7. 安装 Systemd 服务 ====================
echo -e "${GREEN}[6/8] 配置 systemd 后台服务...${RESET}"
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=BWG VPS Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$INSTALL_DIR/.env
ExecStart=$INSTALL_DIR/.venv/bin/python -m app.main
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# ==================== 8. 启动服务 ====================
echo -e "${GREEN}[7/8] 启动 $SERVICE_NAME 服务...${RESET}"
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

echo -e "${GREEN}[8/8] 安装全部完成！${RESET}"
echo -e "${BLUE}====================================================${RESET}"
echo -e "${GREEN}恭喜！BWG VPS Telegram Bot 已经成功部署并在后台运行。${RESET}"
echo -e ""
echo -e "${YELLOW}📝 接下来该做什么？${RESET}"
echo -e "  1. 打开 Telegram，找到你的机器人并发送 ${GREEN}/start${RESET}"
echo -e "  2. 通过菜单里的 ${GREEN}[➕ 添加 VPS]${RESET} 功能绑定你的机器。"
echo -e "  *(提示: VEID 和 API_KEY 会保存在本地 SQLite 数据库中，并在界面和日志中脱敏显示)*"
echo -e ""
echo -e "${YELLOW}💡 常用运维命令 (你可以随时复制执行)：${RESET}"
echo -e "  查看服务运行状态 : ${BLUE}sudo systemctl status $SERVICE_NAME --no-pager${RESET}"
echo -e "  实时查看运行日志 : ${BLUE}sudo journalctl -u $SERVICE_NAME -f${RESET}"
echo -e "  重启机器人服务   : ${BLUE}sudo systemctl restart $SERVICE_NAME${RESET}"
echo -e "  修改配置文件     : ${BLUE}sudo nano $INSTALL_DIR/.env${RESET}"
echo -e "${BLUE}====================================================${RESET}"
echo -e "${RED}⚠️ 注意事项：${RESET}"
echo -e "  curl 一键安装命令只有在代码已经 push 到 GitHub main 分支以后才可用。"
echo -e "  如果 GitHub 仓库还是空的，请先在本地测试无误后完成 git push 操作。"
echo -e "${BLUE}====================================================${RESET}"
