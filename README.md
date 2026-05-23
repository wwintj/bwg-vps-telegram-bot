[中文文档](README.zh-CN.md)

# BWG VPS Telegram Bot

A Telegram bot for managing and monitoring multiple BandwagonHost / KiwiVM VPS instances.

---

## Project Introduction

This project provides a self-hosted Telegram bot that acts as a lightweight client for the BandwagonHost (KiwiVM) API. It allows server administrators to check bandwidth usage, monitor server status, and execute power operations directly from within Telegram without logging into the web panel.

---

## Features

- **Manage Multiple VPS Instances**: Add and monitor multiple BandwagonHost servers within a single bot interface.

- **Admin-Only Access**: Strict authorization check ensuring only configured Telegram User IDs can access the bot commands and menus.

- **Query Traffic Usage**: Real-time retrieval of monthly data consumption, total limits, and usage percentages.

- **Query Next Traffic Reset Time**: Shows the exact date and time when your monthly bandwidth allocation resets.

- **Query VPS Status**: Check the current operational status of your instances.

- **Query Expiry Date**: Display the contract expiry date if manually configured during initialization.

- **Start VPS**: Power on your virtual machine via API.

- **Stop VPS**: Perform a graceful shutdown of the instance.

- **Restart VPS**: Reboot the operating system via KiwiVM control commands.

- **Kill VPS with Confirmation**: Force power off a frozen server with a two-step confirmation wrapper to prevent accidental data loss.

- **Add / Edit / Delete VPS**: Complete life-cycle management of your monitored nodes right from the text UI.

---

## Security Notice

- **Minimalist Environment Provisioning**: The installer only asks for global environment flags (`TELEGRAM_BOT_TOKEN`, `ADMIN_USER_IDS`, and `TIMEZONE`).

- **No Privilege Leaks in Config**: The installation script does not ask for your BandwagonHost VEID or API_KEY. High-privilege API credentials are added later inside the running Telegram Bot menu.

- **Asset Database Isolation**: VEID and API_KEY are stored in the local SQLite database and are masked in the UI panels and application logs to safeguard privacy.

- **Strict Git Exclusions**: The `.env` configuration file, the `data/bot.db` production binary, and the `backups/` directory are locked under Git exclusion rules and must never be committed to GitHub.

---

## Requirements

- **Operating System**: Ubuntu 22.04 / Ubuntu 24.04 / Debian 11 / Debian 12

- **Python Runtime**: Python 3.10+ with `venv` package support

- **Telegram Bot Credentials**: A token generated via @BotFather and your active numerical account User ID

- **KiwiVM API Credentials**: The unique VEID and API_KEY for each BandwagonHost instance you wish to manage

---

## Installation Methods

### Method 1: Local Git Clone

Recommended for standard deployments and manual source control tracking.

```bash
git clone [https://github.com/wwintj/bwg-vps-telegram-bot.git](https://github.com/wwintj/bwg-vps-telegram-bot.git)
cd bwg-vps-telegram-bot
sudo bash install.sh
