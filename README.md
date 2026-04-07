# WhatsApp Shift Bot 🤖

A professional Selenium-based automation tool designed to monitor WhatsApp groups for shift-related requests and automatically manage responses and notifications.

## 🚀 Features

- **Real-time Monitoring**: Scans a specific WhatsApp group for incoming messages matching predefined keywords.
- **Instant Response**: Automatically replies with "Ok" (or any configured text) to matching messages.
- **Reaction Detection**: Waits for a user reaction (like, heart, etc.) on the bot's reply before proceeding.
- **Secondary Notifications**: Once a reaction is detected, it switches to a secondary group to send a follow-up notification.
- **Session Persistence**: Uses a custom Chrome profile (`chrome-data`) to keep you logged in between sessions.
- **Smart Detection**: Uses highly optimized JavaScript injection for low-latency message detection.

## 🛠️ Prerequisites

- **Python 3.8+**
- **Google Chrome** (installed on your system)
- **ChromeDriver** (automatically managed by `webdriver-manager`)

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd whatsapp-bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

You can customize the bot's behavior directly in `bot.py`:

- `GROUP_NAME`: The name of the primary WhatsApp group to monitor (e.g., "Support Shift").
- `TARGET_KEYWORDS`: A list of keywords that trigger the bot (e.g., "shift", "cover", "anyone").
- `REPLY_TEXT`: The message sent as an initial response (default: "Ok").
- `SECOND_GROUP_NAME`: The group to notify after a reaction is received.
- `NOTIFY_MESSAGE`: The message sent to the second group.

## 🚀 Usage

1. **Run the bot**:
   ```bash
   python bot.py
   ```

2. **Login**:
   - On the first run, a Chrome window will open.
   - Scan the QR code with your WhatsApp app.
   - Press **ENTER** in the terminal once you are logged in.

3. **Operation**:
   - The bot will search for and open the target group.
   - It will stay in the target group and wait for new messages.
   - If a matching message arrives, it replies instantly and waits for a reaction.
   - Once a reaction is received, it notifies the secondary group and returns to the primary group.

## ⚠️ Important Notes

- **Headless Mode**: The current version runs with a visible browser window to handle the initial QR scan and visual monitoring.
- **Permissions**: Ensure you have the necessary permissions to use automation on the groups you are monitoring.
- **Safety**: WhatsApp's terms of service prohibit certain types of automation. Use this tool responsibly.

## 📂 Project Structure

- `bot.py`: The main automation script.
- `requirements.txt`: Python package dependencies.
- `chrome-data/`: Directory where the Chrome profile and session data are stored.
- `Support-whatsapp.pem`: AWS authentication file (if applicable for deployment).

---
*Created with ❤️ for efficient shift management.*
