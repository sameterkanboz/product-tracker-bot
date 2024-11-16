import requests
import re
import schedule
import time
from telegram import Bot, Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from telegram.error import TelegramError
from flask import Flask
from threading import Thread

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Telegram Bot configuration (from .env file)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Get the token from .env
CHAT_ID = os.getenv("CHAT_ID")  # Get the chat ID from .env

if not TELEGRAM_TOKEN or not CHAT_ID:
    raise ValueError("TELEGRAM_TOKEN or CHAT_ID is missing in .env file")

# Initialize the bot
bot = Bot(token=TELEGRAM_TOKEN)
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Flask app for keep-alive
app = Flask('')


@app.route('/')
def home():
    return "Bot is running!"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()


# Track the latest product URL sent by the user
latest_product_url = None


def extract_product_id(url):
    match = re.search(r'/(\d{14})/', url)
    return match.group(1) if match else None


def fetch_relevant_product_data(product_url):
    product_id = extract_product_id(product_url)
    if not product_id:
        return "Invalid URL: Could not find product ID."

    api_url = f"https://www.deichmann.com/TR/tr/shop/ws/restapi/v1/product/{product_id}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        product_data = response.json()

        # Extract necessary fields
        price = product_data.get("price", {}).get("formattedValue", "N/A")
        currency = product_data.get("price", {}).get("currency",
                                                     {}).get("symbol", "TL")
        variants = product_data.get("variants", [])

        # Create a readable message
        message = f"🛍️ **Ürün Takibi Başlatıldı!**\n\n"
        message += f"**Ürün Adı**: {product_data.get('name', 'Ürün adı mevcut değil')}\n"
        message += f"**Fiyat**: {price} {currency}\n\n"
        message += "📏 **Mevcut Bedenler ve Stok Durumu:**\n"

        # Add each variant with stock and size details
        in_stock_variants = [
            f"- Beden: {variant['size']['value']} - Renk: {variant['color']['name']} ✅ Stokta"
            for variant in variants if variant["available"]
        ]
        out_of_stock_variants = [
            f"- Beden: {variant['size']['value']} - Renk: {variant['color']['name']} ❌ Stokta yok"
            for variant in variants if not variant["available"]
        ]

        if in_stock_variants:
            message += "\n".join(in_stock_variants) + "\n"
        if out_of_stock_variants:
            message += "\n".join(out_of_stock_variants) + "\n"

        # Final message with product info and variants
        return message

    except requests.exceptions.HTTPError as err:
        return f"HTTP error occurred: {err}"
    except Exception as err:
        return f"Other error occurred: {err}"


def send_product_data():
    global latest_product_url
    if not latest_product_url:
        print("No product URL set for tracking.")
        return

    data_message = fetch_relevant_product_data(latest_product_url)

    try:
        bot.send_message(chat_id=CHAT_ID,
                         text=data_message,
                         parse_mode='Markdown')
        print("Message sent successfully")
    except TelegramError as e:
        print(f"Failed to send message: {e}")


def handle_message(update: Update, context: CallbackContext):
    global latest_product_url
    user_message = update.message.text
    product_id = extract_product_id(user_message)

    if product_id:
        latest_product_url = user_message
        update.message.reply_text(
            f"Tracking updated for product: {latest_product_url}")
        # Send product info right away after receiving the URL
        send_product_data()
    else:
        update.message.reply_text("Please send a valid product URL.")


# Setup scheduled job to send product data every hour
schedule.every().hour.at(":00").do(lambda: send_product_data())

# Register handlers
dispatcher.add_handler(
    MessageHandler(Filters.text & ~Filters.command, handle_message))

if __name__ == "__main__":
    # Start the Flask app for keep-alive
    keep_alive()
    # Start polling for updates
    updater.start_polling()
    print("Bot started. Send a product URL to track it once.")
    # Run scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(1)
