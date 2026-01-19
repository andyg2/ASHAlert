# Awesome Selfhosted Monitor

A lightweight Python-based monitoring tool that tracks the [awesome-selfhosted](https://github.com/awesome-selfhosted/awesome-selfhosted) repository. It identifies newly added projects by comparing the current `README.md` against a local state and sends detailed notifications directly to your Telegram.

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- **Automated Tracking**: Periodically checks for changes in the master list.
- **Smart Diffing**: Intelligently extracts only the newly added lines.
- **Rich Notifications**: Parses Markdown entries to send clean Telegram alerts including:
  - Project Name & Link
  - Description
  - Demo and Source Code links (if available)
  - License and Deployment info (Docker, etc.)
- **API Friendly**: Uses GitHub's raw content URLs to avoid GitHub API rate limiting.
- **State Management**: Maintains a local copy of the README to ensure you never get duplicate alerts.

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.10 or higher.
- A Telegram Bot (created via [@BotFather](https://t.me/botfather)).
- Your Telegram User ID (can be found via [@userinfobot](https://t.me/userinfobot)).

### 2. Installation

Clone this repository and navigate to the project folder:

```bash
git clone https://github.com/yourusername/ash-monitor.git
cd ash-monitor
```

Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file in the root directory:

```ini
# Telegram Configuration
TELEGRAM_BOT_TOKEN=123456789:ABCDefGhIJKlmNoPQRstuVwXyz
TELEGRAM_CHAT_ID=987654321

# Optional Customization
STATE_DIR=./state
GITHUB_OWNER=awesome-selfhosted
GITHUB_REPO=awesome-selfhosted
GITHUB_BRANCH=master
```

## 🛠 Usage

To run the script manually:

```bash
python app.py
```

### Example Telegram Alert

<img width="467" height="602" alt="ash-alert" src="https://github.com/user-attachments/assets/81e01cec-b090-47a0-a1f0-c7bd3e8fc21d" />


### First Run Behavior

On the first execution, the script will download the current `README.md` and save it as a "baseline" in the `/state` folder. **It will not send notifications for existing projects.** Notifications will only trigger when the remote file changes after the baseline is established.

## 🕒 Automation (Windows Deployment)

To have this run automatically on Windows without keeping a console window open use pythonw

### Import the Sample Task

Open Task Scheduler in Windows and import the scheduled-task-sample.xml

### Manual Setup

Set up a batch file to lanch the script

1. Create a file named `run_monitor.bat`:

```batch
@echo off
cd /d "C:\Path\To\Your\Project"
".\venv\Scripts\pythonw.exe" "app.py"
```

2. Open **Windows Task Scheduler**.
3. Create a **Basic Task** named "ASH Monitor".
4. Set the Trigger to **Daily** or **Multiple times a day**.
5. Set the Action to **Start a Program** and point it to your `.bat` file.
6. Under properties, select **Run whether user is logged on or not** to run it silently in the background.

## 📦 How it Works

1. **Fetch**: Downloads the latest `README.md` from the GitHub master branch.
2. **Compare**: Uses `difflib` to compare the new version against the last saved version.
3. **Parse**: Uses Regex to extract metadata (links, descriptions, tags) from the specific Markdown formatting used in the Awesome list.
4. **Notify**: Uses an asynchronous Telegram client to push alerts to your device.

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).

---
*Disclaimer: This project is not officially affiliated with the awesome-selfhosted maintainers.*
