[English](README.md)

# BWG VPS Telegram Bot

一个用于管理和监控多台搬瓦工 (BandwagonHost / KiwiVM) VPS 实例的 Telegram 机器人。

## 项目介绍

本项目提供了一个可自行部署的 Telegram 机器人，作为搬瓦工 (KiwiVM) API 的轻量级客户端。它允许服务器管理员直接在 Telegram 中查看流量使用情况、监控服务器状态并执行电源操作，而无需登录网页控制面板。

## 功能列表

- 从 Telegram 菜单添加 VPS
- 编辑 VPS
- 删除 VPS
- 查询流量使用情况
- 查询下次流量重置时间
- 查询 VPS 状态
- 查询到期时间（如果在初始化时手动配置）
- 开机 (Start VPS)
- 关机 (Stop VPS)
- 重启 (Restart VPS)
- 强制关机 (Kill VPS，含二次确认保护)
- 管理多台 VPS 实例
- 仅限管理员访问

## 安全说明

- 安装程序仅要求输入 `TELEGRAM_BOT_TOKEN`、`ADMIN_USER_IDS` 和 `TIMEZONE`。
- 安装程序不会要求输入搬瓦工的 VEID 或 API_KEY。
- VEID 和 API_KEY 是在 Bot 启动后，在 Telegram 菜单内添加的。
- 绝对不要将 `.env` 提交到 GitHub 仓库。
- 绝对不要将 `data/bot.db` 提交到 GitHub 仓库。
- 绝对不要将 `backups/` 提交到 GitHub 仓库。
- VEID 和 API_KEY 保存在本地 SQLite 数据库中，并应在界面和日志中脱敏显示。

## 系统要求

- Ubuntu 22.04 / Ubuntu 24.04 / Debian 11 / Debian 12
- Python 3.10+
- Telegram Bot Token
- Telegram User ID
- 每台待管理 VPS 的搬瓦工 / KiwiVM VEID 和 API_KEY

## 安装方式

### 方式一：本地 Git Clone

```bash
git clone https://github.com/wwintj/bwg-vps-telegram-bot.git
cd bwg-vps-telegram-bot
sudo bash install.sh
```

### 方式二：Curl 一键安装脚本

*请注意：curl 安装方式只有在项目文件已经推送到 GitHub main 分支后才可用。*

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/wwintj/bwg-vps-telegram-bot/main/install.sh)
```

## 安装脚本会要求输入什么

- `TELEGRAM_BOT_TOKEN`
- `ADMIN_USER_IDS`
- `TIMEZONE`

## 安装脚本不会要求输入什么

- BandwagonHost VEID
- BandwagonHost API_KEY

## 配置文件位置

`/opt/bwg-vps-telegram-bot/.env`

## 数据库位置

`/opt/bwg-vps-telegram-bot/data/bot.db`

## 如何获取前置信息

### 如何获取 Telegram Bot Token
通过 @BotFather 获取。

### 如何获取 Telegram User ID
可以通过 @userinfobot 或类似机器人获取。

### 如何获取 BandwagonHost VEID 和 API_KEY
登录搬瓦工 (BandwagonHost / KiwiVM) 控制面板，在对应 VPS 的 API 页面查看。

## 安装后如何使用

1. 打开 Telegram
2. 向机器人发送 `/start`
3. 使用“添加 VPS”菜单
4. 输入 VPS 名称
5. 输入 VEID
6. 输入 API_KEY
7. 查询流量、状态、重置时间和到期时间
8. 执行开机、关机、重启或强制关机（含确认步骤）

## systemd 服务管理命令

```bash
sudo systemctl status bwg-vps-telegram-bot --no-pager
sudo journalctl -u bwg-vps-telegram-bot -f
sudo systemctl restart bwg-vps-telegram-bot
sudo systemctl stop bwg-vps-telegram-bot
```

## 更新方法

```bash
cd /opt/bwg-vps-telegram-bot
sudo bash update.sh
```

## 卸载方法

```bash
cd /opt/bwg-vps-telegram-bot
sudo bash uninstall.sh
```

- **普通卸载**：删除 systemd 服务，但保留 `.env` 和 `data/bot.db`。
- **完全卸载**：在输入 DELETE 后彻底删除所有内容。

## 项目结构

```text
bwg-vps-telegram-bot/
├── .env.example
├── .gitignore
├── README.md
├── README.zh-CN.md
├── install.sh
├── uninstall.sh
├── update.sh
├── requirements.txt
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── utils.py
│   ├── handlers/
│   │   ├── start.py
│   │   ├── vps_manage.py
│   │   ├── query.py
│   │   └── control.py
│   ├── services/
│   │   ├── kiwivm_client.py
│   │   └── formatter.py
│   └── repositories/
│       └── vps_repository.py
└── data/
    └── .gitkeep
```

## 常见问题

- **机器人没反应**：检查 Bot Token 是否正确，以及服务器能否正常访问 Telegram API。
- **没有权限**：确保你的 Telegram User ID 正确填写在了 `ADMIN_USER_IDS` 中。
- **Telegram User ID 错误**：通过 @userinfobot 重新确认你的 ID。
- **systemd 服务启动失败**：使用 `journalctl` 查看日志，排查 Python 依赖或环境错误。
- **GitHub curl 一键安装失败**：请确保仓库设置为公开状态，且 `install.sh` 已经推送到了 `main` 分支。
- **SQLite 数据库权限问题**：确保 `/opt/bwg-vps-telegram-bot/data` 目录拥有正确的写入权限。
- **搬瓦工 API 错误**：检查 VEID 和 API_KEY 是否正确，或者该 VPS 是否已被官方暂停。

## License

MIT License
