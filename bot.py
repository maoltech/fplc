import sqlite3
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, CallbackContext
)
import logging
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve environment variables
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_USER_ID'))

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
conn = sqlite3.connect('wallets.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS wallets (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    fpl_tag TEXT,
    balance INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1
)
''')
conn.commit()

# Command to start the bot and create a wallet
async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    username = update.effective_user.username

    cursor.execute('SELECT * FROM wallets WHERE user_id = ?', (user_id,))
    if cursor.fetchone():
        await update.message.reply_text("You already have a wallet!")
    else:
        await update.message.reply_text("Welcome! Please provide your FPL tag by sending a message.")

        # Store user data and wait for the FPL tag
        context.user_data['awaiting_fpl_tag'] = True

# Handle the FPL tag input
async def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    username = update.effective_user.username
    message_text = update.message.text

    if context.user_data.get('awaiting_fpl_tag'):
        # Save the FPL tag and create the wallet
        cursor.execute('INSERT INTO wallets (user_id, username, fpl_tag) VALUES (?, ?, ?)', (user_id, username, message_text))
        conn.commit()

        # Disable awaiting state
        context.user_data['awaiting_fpl_tag'] = False

        await update.message.reply_text(f"Wallet created successfully with FPL tag: {message_text}!")

# Command for the admin to send coins
async def send_coins(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("You are not authorized to send coins.")
        return

    try:
        username = context.args[0]
        amount = int(context.args[1])

        cursor.execute('SELECT * FROM wallets WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user:
            new_balance = user[3] + amount
            cursor.execute('UPDATE wallets SET balance = ? WHERE username = ?', (new_balance, username))
            conn.commit()
            await update.message.reply_text(f"Sent {amount} coins to {username}. New balance: {new_balance}")
        else:
            await update.message.reply_text("User not found.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /send_coins <username> <amount>")

# Command to check balance
async def balance(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    cursor.execute('SELECT balance FROM wallets WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()

    if user:
        await update.message.reply_text(f"Your balance is: {user[0]} coins.")
    else:
        await update.message.reply_text("You do not have a wallet. Use /start to create one.")

# Function to send coins automatically every specific period
async def distribute_periodic_coins(context: CallbackContext):
    cursor.execute('SELECT username, balance, is_active FROM wallets')
    users = cursor.fetchall()
    periodic_amount = 10  # Define the amount to be sent periodically

    for user in users:
        if user[2]:  # Check if the user is active
            new_balance = user[1] + periodic_amount
            cursor.execute('UPDATE wallets SET balance = ? WHERE username = ?', (new_balance, user[0]))
            conn.commit()

    logger.info("Periodic coins distributed.")

def main():
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("send_coins", send_coins))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Schedule the periodic coin distribution
    job_queue = application.job_queue
    job_queue.run_repeating(distribute_periodic_coins, interval=7*24*60*60, first=0)  # Every week (adjust interval as needed)

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
