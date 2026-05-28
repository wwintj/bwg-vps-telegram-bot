# BWG VPS Telegram Bot

一个用于管理和监控 BandwagonHost / KiwiVM VPS 的 Telegram 机器人。

## 项目简介

本项目提供一个可自托管的 Telegram 机器人，用作 BandwagonHost / KiwiVM API 的轻量客户端。管理员可以在 Telegram 中管理多台 VPS、查看服务器信息，并执行常见的电源操作。

## 当前已实现

- Telegram Bot 基础启动入口
- `.env` 配置读取
- 管理员 ID 白名单校验
- SQLite 数据库初始化
- VPS 数据表结构与平滑字段升级
- `/start` 主菜单
- 添加 VPS
- 删除 VPS
- VPS 列表
- 查询单台 VPS 流量与配置信息
- 查询全部 VPS 概况
- 开机
- 关机
- 重启
- 强制关机，并加入二次确认
- 迁移机房，并加入二次确认
- SSH 端口连通性探测
- Ubuntu / Debian 一键安装脚本
- systemd 服务部署脚本
- 更新脚本与卸载脚本

## 后续可增强功能

- 编辑 VPS
- 定时流量提醒
- 到期时间提醒
- 流量使用率阈值告警
- API_KEY 加密存储
- 更细粒度的管理员权限

## 安全说明

- 安装脚本只要求输入 `TELEGRAM_BOT_TOKEN`、`ADMIN_USER_IDS` 和 `TIMEZONE`。
- 安装脚本不会要求输入 BandwagonHost / KiwiVM 的 `VEID` 或 `API_KEY`。
- `VEID` 和 `API_KEY` 应在机器人功能中添加，并保存在本地 SQLite 数据库。
- 不要提交 `.env`。
- 不要提交 `data/bot.db`。
- 不要提交 `backups/`。
- 日志和界面中应避免明文展示 `API_KEY`。

## 系统要求

- Ubuntu 22.04 / Ubuntu 24.04 / Debian 11 / Debian 12
- Python 3.10+
- Telegram Bot Token
- Telegram 管理员 User ID
- 每台 VPS 的 BandwagonHost / KiwiVM `VEID` 和 `API_KEY`

## 安装方式

### 本地克隆安装

```bash
git clone https://github.com/wwintj/bwg-vps-telegram-bot.git
cd bwg-vps-telegram-bot
sudo bash install.sh
```

### 一键脚本安装

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/wwintj/bwg-vps-telegram-bot/main/install.sh)
```

## 安装脚本会要求输入

- `TELEGRAM_BOT_TOKEN`
- `ADMIN_USER_IDS`
- `TIMEZONE`

## 安装脚本不会要求输入

- BandwagonHost / KiwiVM `VEID`
- BandwagonHost / KiwiVM `API_KEY`

## 配置文件

默认配置文件位置：

```text
/opt/bwg-vps-telegram-bot/.env
```

示例配置：

```env
TELEGRAM_BOT_TOKEN=
ADMIN_USER_IDS=
DATABASE_PATH=./data/bot.db
TIMEZONE=Asia/Shanghai
KIWIVM_API_BASE=https://api.64clouds.com/v1
LOG_LEVEL=INFO
REQUEST_TIMEOUT=20
```

## 数据库

默认数据库位置：

```text
/opt/bwg-vps-telegram-bot/data/bot.db
```

当前 `vps_instances` 表字段：

- `id`
- `name`
- `veid`
- `api_key`
- `ssh_port`
- `note`
- `expiry_date`

## 使用方式

安装并启动服务后，在 Telegram 中向机器人发送：

```text
/start
```

当前版本支持添加 VPS、查看 VPS 列表、查询流量、查询全部 VPS 概况，以及执行开机、关机、重启、强制关机和机房迁移操作。

## systemd 服务管理

```bash
sudo systemctl status bwg-vps-telegram-bot --no-pager
sudo journalctl -u bwg-vps-telegram-bot -f
sudo systemctl restart bwg-vps-telegram-bot
sudo systemctl stop bwg-vps-telegram-bot
```

## 更新

```bash
cd /opt/bwg-vps-telegram-bot
sudo bash update.sh
```

更新脚本会在拉取最新代码前备份 `.env` 和 `data/`。

## 卸载

```bash
cd /opt/bwg-vps-telegram-bot
sudo bash uninstall.sh
```

- 普通卸载：删除 systemd 服务，保留 `.env` 和 `data/bot.db`。
- 完全卸载：确认后删除安装目录和本地数据。

## 项目结构

```text
bwg-vps-telegram-bot/
├── .env.example
├── .gitignore
├── README.md
├── install.sh
├── uninstall.sh
├── update.sh
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── utils.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── start.py
│   │   ├── vps_manage.py
│   │   ├── query.py
│   │   └── control.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── vps_repository.py
│   └── services/
│       ├── __init__.py
│       ├── formatter.py
│       └── kiwivm_client.py
└── data/
    └── .gitkeep
```

## 常见问题

### 机器人没有响应

检查 `TELEGRAM_BOT_TOKEN` 是否正确，并确认服务器可以访问 Telegram API。

### 提示没有权限

确认你的 Telegram User ID 已正确填写到 `ADMIN_USER_IDS` 中。多个管理员请使用英文逗号分隔。

### 服务启动失败

使用以下命令查看日志：

```bash
sudo journalctl -u bwg-vps-telegram-bot -f
```

### SQLite 权限错误

确认 `data/` 目录存在，并且运行服务的用户有写入权限。

## 许可证

MIT License
