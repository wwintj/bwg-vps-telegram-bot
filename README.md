[中文文档](README.zh-CN.md)

# BWG VPS Telegram Bot

A Telegram bot for managing and monitoring multiple BandwagonHost / KiwiVM VPS instances.

## Project Introduction

This project provides a self-hosted Telegram bot that acts as a lightweight client for the BandwagonHost (KiwiVM) API. It allows server administrators to check bandwidth usage, monitor server status, and execute power operations directly from within Telegram without logging into the web panel.

## Features

- Add VPS from Telegram menu
- Edit VPS
- Delete VPS
- Query traffic usage
- Query next traffic reset time
- Query VPS status
- Query expiry date if manually configured
- Start VPS
- Stop VPS
- Restart VPS
- Kill VPS with confirmation
- Manage multiple VPS instances
- Admin-only access

## Security Notice

- The installer only asks for `TELEGRAM_BOT_TOKEN`, `ADMIN_USER_IDS`, and `TIMEZONE`.
- The installer does not ask for BandwagonHost VEID or API_KEY.
- VEID and API_KEY are added later inside the Telegram Bot menu.
- `.env` must never be committed.
- `data/bot.db` must never be committed.
- `backups/` must never be committed.
- VEID and API_KEY are stored in the local SQLite database and should be masked in UI and logs.

## Requirements

- Ubuntu 22.04 / Ubuntu 24.04 / Debian 11 / Debian 12
- Python 3.10+
- Telegram Bot Token
- Telegram User ID
- BandwagonHost / KiwiVM VEID and API_KEY for each VPS

## Installation Methods

### Method 1: Local Git Clone

```bash
git clone https://github.com/wwintj/bwg-vps-telegram-bot.git
cd bwg-vps-telegram-bot
sudo bash install.sh
```

### Method 2: Curl One-Click Script

*Please note: The curl installation method only works after the project files have been pushed to the GitHub main branch.*

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/wwintj/bwg-vps-telegram-bot/main/install.sh)
```

## What the Installer Asks For

- `TELEGRAM_BOT_TOKEN`
- `ADMIN_USER_IDS`
- `TIMEZONE`

## What the Installer Does Not Ask For

- BandwagonHost VEID
- BandwagonHost API_KEY

## Configuration File Location

`/opt/bwg-vps-telegram-bot/.env`

## Database Location

`/opt/bwg-vps-telegram-bot/data/bot.db`

## Prerequisites Procurement Guide

### How to get Telegram Bot Token
Use @BotFather.

### How to get Telegram User ID
Use @userinfobot or a similar bot.

### How to get BandwagonHost VEID and API_KEY
Log in to BandwagonHost / KiwiVM control panel and check the API page for each VPS.

## Usage After Installation

1. Open Telegram
2. Send `/start` to the bot
3. Use Add VPS menu
4. Enter VPS name
5. Enter VEID
6. Enter API_KEY
7. Query traffic, status, reset time, expiry date
8. Start, stop, restart, or kill VPS with confirmation

## Service Management Commands

```bash
sudo systemctl status bwg-vps-telegram-bot --no-pager
sudo journalctl -u bwg-vps-telegram-bot -f
sudo systemctl restart bwg-vps-telegram-bot
sudo systemctl stop bwg-vps-telegram-bot
```

## Update

```bash
cd /opt/bwg-vps-telegram-bot
sudo bash update.sh
```

## Uninstall

```bash
cd /opt/bwg-vps-telegram-bot
sudo bash uninstall.sh
```

- **Normal uninstall**: removes the systemd service but keeps `.env` and `data/bot.db`.
- **Full uninstall**: removes everything after typing DELETE.

## Project Structure

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

## Troubleshooting

- **Bot does not respond**: Check if the bot token is correct and if the server can access Telegram API.
- **Permission denied**: Ensure your Telegram User ID is correctly listed in `ADMIN_USER_IDS`.
- **Wrong Telegram User ID**: Verify your ID with @userinfobot.
- **systemd service failed**: Check the logs using `journalctl` to identify Python or environment errors.
- **GitHub curl install fails**: Ensure the repository is public and the `install.sh` file exists on the `main` branch.
- **SQLite database permission issue**: Ensure the `/opt/bwg-vps-telegram-bot/data` directory has the correct write permissions.
- **BandwagonHost API error**: Check if your VEID and API_KEY are correct and if your VPS is suspended.

## License

MIT License
