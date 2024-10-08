# Fantasy Premier League Telegram Bot

A Telegram bot that interacts with users to manage virtual wallets and coins, tailored for Fantasy Premier League (FPL) enthusiasts. This bot allows users to create wallets, check their balance, and receive periodic coin distributions. Admins can send coins to users.

## Features

- **Create Wallet**: Users can create a wallet by providing their FPL tag.
- **Check Balance**: Users can check their wallet balance.
- **Send Coins**: Admins can send coins to users.
- **Periodic Distribution**: Automatic periodic coin distribution to all active users.

## Installation

### Prerequisites

- Python 3.7 or higher
- `python-telegram-bot` library with job-queue support
- SQLite database

### Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/fpl-telegram-bot.git
   cd fpl-telegram-bot
    ```

2. **Install Dependencies**

Create a virtual environment (optional) and install the required packages:

    ```bash
        python -m venv venv
        source venv/bin/activate  # On Windows use `venv\Scripts\activate`
        pip install -r requirements.txt
        Create .env File
    ```
Create a .env file in the root directory of the project and add the following environment variables:

TELEGRAM_BOT_TOKEN=your_telegram_bot_token
ADMIN_USER_ID=your_telegram_user_id
TELEGRAM_BOT_TOKEN: The token for your Telegram bot (get it from BotFather).
ADMIN_USER_ID: Your Telegram user ID for admin commands.
Run the Bot

```bash
python bot.py
```