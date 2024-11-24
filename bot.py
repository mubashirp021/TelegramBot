import os
import time
import telebot
from dotenv import load_dotenv
from datetime import datetime, timedelta
import threading

# Load environment variables from .env file
load_dotenv()

# Get the bot token from environment variable
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    print("Error: BOT_TOKEN is not set.")
    exit(1)

# Initialize the bot with the token
bot = telebot.TeleBot(BOT_TOKEN)

# A dictionary to store reminders
reminders = {}

# Function to handle /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to the Reminder Bot! To set a reminder, use the command /remind <time> <message>.\nFor example: /remind 10m Take a break!")

# Function to handle /remind command
@bot.message_handler(commands=['remind'])
def set_reminder(message):
    try:
        # Extract the reminder time and message from the command
        parts = message.text.split(" ", 2)
        if len(parts) < 3:
            bot.reply_to(message, "Please use the format: /remind <time> <message>")
            return

        time_str = parts[1]
        reminder_message = parts[2]

        # Parse the time string (e.g., 10m, 1h)
        reminder_time = parse_time(time_str)
        if reminder_time is None:
            bot.reply_to(message, "Invalid time format. Please use m for minutes or h for hours.")
            return
        
        reminder_time_str = str(reminder_time)

        # Store the reminder
        reminder_time = datetime.now() + reminder_time
        reminders[message.chat.id] = (reminder_time, reminder_message)

        bot.reply_to(message, f"Reminder set! I'll remind you in {reminder_time_str}.")
        
        # Start a separate thread to send the reminder at the right time
        threading.Thread(target=reminder_worker, args=(message.chat.id, reminder_time, reminder_message)).start()

    except Exception as e:
        print(e)
        bot.reply_to(message, "There was an error setting your reminder.")

# Function to parse time in "10m" or "1h" format
def parse_time(time_str):
    """Parse time strings like '10m', '1h' to timedelta objects."""
    if time_str.endswith('m'):
        try:
            minutes = int(time_str[:-1])
            return timedelta(minutes=minutes)
        except ValueError:
            return None
    elif time_str.endswith('h'):
        try:
            hours = int(time_str[:-1])
            return timedelta(hours=hours)
        except ValueError:
            return None
    return None

# Function to handle sending the reminder
def reminder_worker(chat_id, reminder_time, reminder_message):
    """Wait until the reminder time and then send the reminder."""
    # Wait for the reminder time
    time_to_wait = (reminder_time - datetime.now()).total_seconds()
    if time_to_wait > 0:
        time.sleep(time_to_wait)
    
    # Send the reminder
    bot.send_message(chat_id, f"Reminder: {reminder_message}")

bot.infinity_polling()