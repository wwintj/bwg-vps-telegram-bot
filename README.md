# BWG VPS Telegram Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight, secure, and modern Telegram bot for managing, monitoring, and controlling multiple BandwagonHost / KiwiVM VPS instances. Built with Python and SQLite, featuring a native 2x2 grid keyboard layout and automated network-level port probing for reliable state confirmation.

---

## 💻 Project Introduction

Managing multiple BandwagonHost VPS instances can be tedious when logging into the official KiwiVM panel repeatedly. This project provides an elegant, admin-only Telegram Bot client interface. It allows you to monitor data usage, verify runtime status, and perform essential power management directly within Telegram, completely independent of the web portal.

---

## ✨ Features

- **Multi-VPS Fleet Management**: Bind, organize, and monitor an unlimited number of BandwagonHost servers.
- **Admin-Only Access**: Strict access control lists (ACL) ensuring only authorized Telegram User IDs can interact with the bot.
- **Real-Time Network Probing**: Instead of relying solely on static API data, the bot performs live TCP handshakes on your custom SSH ports to verify if a VPS is truly `Running` or `Stopped`.
- **Power Operations**: Support for Boot (`Start`), Shutdown (`Stop`), Restart (`Restart`), and Force Power-Off (`Kill`) with active safety confirmations.
- **Data Usage Analytics**: Query current monthly data counter, bandwidth multipliers, total pool limit, and precise next data reset timestamps.
- **Data Center Migration Guide**: Trigger the official `Migrate to another datacenter` panel wizard directly inside Telegram to safely switch nodes/IPs.
- **Modern UI**: Clean 2x2 multi-grid layout with uniform emoji styling for perfectly aligned vertical data presentation across all desktop and mobile screens.

---

## 🔒 Security Notice & Best Practices

Security is the highest priority for server monitoring tools. This bot follows strict isolation design principles:
- **Zero Sourcing Leakage**: The core installation environment only asks for the Telegram Bot Token and Admin User IDs.
- **Isolated Asset Database**: BandwagonHost **VEID** and **API Keys** are **NEVER** stored in the plain `.env` text file. They are added post-installation directly within the secure chat menu and kept safely inside a local SQLite database.
- **Automatic Masking**: High-privilege API Keys, VEIDs, and sensitive information are automatically masked (e.g., `abc1********xyz9`) in all log files and UI rendering panels.
- **Hardened Permissions**: The installer automatically locks the configurations to `chmod 600` (read/write only by root) and the database directory to `chmod 700`.

---

## 📂 Project Structure

```text
bwg-vps-telegram-bot/
├── .env.example          # Environment variable template for global configurations
├── .gitignore            # Git exclusion definitions protecting sensitive assets
├── README.md             # Project documentation and setup guide
├── install.sh            # Automated lifecycle provisioning environment installer
├── uninstall.sh          # Native cleanup utility supporting normal/purge routines
├── update.sh             # Smooth version pull manager with auto-backup states
├── requirements.txt      # Python dependencies manifest
├── app/                  # Main core service architecture
│   ├── main.py           # Application bootstrap and router gateway
│   ├── config.py         # OS Environment compiler
│   ├── database.py       # Async sqlite database initialization engine
│   ├── utils.py          # Authorization and security decorators
│   ├── handlers/         # Interactive UI presentation logic layers
│   │   ├── start.py      # Base 2x2 grid keyboard layout initializer
│   │   ├── vps_manage.py # Form state machine for adding/deleting instances
│   │   ├── query.py      # Fleet bandwidth and network probe orchestrator
│   │   └── control.py    # Runtime execution and datacenter migration engine
│   ├── services/         # Third-party network clients
│   │   ├── kiwivm_client.py  # Asynchronous non-blocking KiwiVM API provider
│   │   └── formatter.py      # Data metric converters
│   └── repositories/
│       └── vps_repository.py # SQLite CRUD abstraction layer
└── data/                 # Directory holding runtime state binaries
    └── .gitkeep          # Repository placeholder ensuring local asset mounts

🛠️ PrerequisitesBefore launching the deployment, prepare the following requirements:Operating System: A clean VPS running Ubuntu 22.04 LTS, Ubuntu 24.04 LTS, Debian 11, or Debian 12.Telegram Bot Token: Open Telegram, search for @BotFather, send /newbot, and copy the given HTTP API Token.Telegram User ID: Search for @userinfobot or similar identity lookups to obtain your numerical unique Telegram ID (e.g., 123456789).KiwiVM Credentials: Log into your BandwagonHost client portal, navigate to your KiwiVM panel, and fetch the VEID and API Key from the panel menu.🚀 Installation MethodsYou can deploy the bot on your Ubuntu/Debian server using either of the following standard methods.Method 1: Local Git Clone (Recommended)Recommended for development and manual version monitoring.Bashgit clone [https://github.com/wwintj/bwg-vps-telegram-bot.git](https://github.com/wwintj/bwg-vps-telegram-bot.git)
cd bwg-vps-telegram-bot
sudo bash install.sh
Method 2: Curl One-Click ScriptNote: The curl script method will only become active after you push the source code repository onto your GitHub main branch.Bashbash <(curl -fsSL [https://raw.githubusercontent.com/wwintj/bwg-vps-telegram-bot/main/install.sh](https://raw.githubusercontent.com/wwintj/bwg-vps-telegram-bot/main/install.sh))
What the Installer Asks For:The installation wizard is completely streamlined. It will ONLY ask for:TELEGRAM_BOT_TOKEN (Hidden echo input for privacy)ADMIN_USER_IDS (Supports multiple admins separated by commas)TIMEZONE (Optional, defaults to Asia/Shanghai)It will NEVER ask for your BandwagonHost VEID or API Key during installation.📖 Usage GuideOnce the installation completes successfully and the systemd service starts running:Initialize Bot: Open Telegram, find your bot, and click or send /start.View Grid Menu: The bot will greet you and unlock the persistent 4-button responsive menu panel:[📊 VPS 列表 (Fleet List)][⚙️ 控制 VPS (Control Panel)][📈 查询流量 (Traffic Statistics)][🌐 查询全部 (Global Overview)]Add Your VPS: Click 📊 VPS 列表, then select ➕ 添加 VPS. The state machine wizard will guide you to type in sequence:Customized display name (e.g., LA-CN2-GIA)KiwiVM VEIDKiwiVM API_KEYUnique custom SSH Port (Manually configured for accurate status probing)Extra metadata note / Expiry date tracking (Optional, enter skip to bypass)Interact: Use the menu to run live TCP probes, read status panels, trigger reboots, or schedule migrations safely.⚙️ Service Management & CommandsThe installer configures a native background unit called bwg-vps-telegram-bot.service. Use standard Linux runtime commands to manage it:Task DescriptionTerminal Administrative CommandCheck Runtime Statussudo systemctl status bwg-vps-telegram-bot --no-pagerStream Live Logssudo journalctl -u bwg-vps-telegram-bot -fRestart Servicesudo systemctl restart bwg-vps-telegram-botStop Background Workersudo systemctl stop bwg-vps-telegram-botModify Core Configssudo nano /opt/bwg-vps-telegram-bot/.env && sudo systemctl restart bwg-vps-telegram-bot🔄 Smooth UpgradesTo upgrade the application without breaking database connections or losing configuration profiles:Bashcd /opt/bwg-vps-telegram-bot
sudo bash update.sh
The update engine automatically generates safe timestamp backups inside /opt/bwg-vps-telegram-bot/backups/ before running pull sequences.❌ UninstallationTo safely dismantle the background services, choose your path via the automated helper script:Bashcd /opt/bwg-vps-telegram-bot
sudo bash uninstall.sh
Normal Uninstall (Option 1): Deletes the systemd background structures but leaves your code, .env file, and data/bot.db database entirely intact for later reinstalls.Full Uninstall (Option 2): Completely purges the entire installation framework. Requires typing the explicit capitalized token DELETE to execute destructive file removals.🔍 Troubleshooting1. Bot Does Not RespondVerify that your server has an active network routing out to Telegram servers (curl -v https://api.telegram.org).Check your live logs using sudo journalctl -u bwg-vps-telegram-bot -f to see if your TELEGRAM_BOT_TOKEN is incorrect.2. Permission Denied / "⛔ 你没有权限使用这个机器人"The Telegram User ID you entered during configuration does not match the account you are texting from. Find your real User ID using @userinfobot and correct it inside /opt/bwg-vps-telegram-bot/.env, then restart the service.3. Systemd Service FailedVerify that your system has python3-venv installed. Run sudo bash install.sh again and select Option 1 to rebuild the virtual environment environment safely.4. Fleet List Always Shows 🔴 StoppedBandwagonHost API does not return accurate container live status flags over standard profiles. Make sure you entered the correct unique custom random SSH Port for that instance when adding it through the menu, as the status checker relies on live TCP ping sweeps.5. SQLite Database File Write FailureEnsure that the /opt/bwg-vps-telegram-bot/data folder has proper root permissions (chmod 700).📄 LicenseDistributed under the MIT License. See LICENSE for more information.
