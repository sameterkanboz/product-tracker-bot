# Product Tracker Bot

This project is a Telegram bot that tracks product availability and sends updates to a specified chat. It uses Flask for keep-alive functionality and integrates with a product API to fetch product details.

## Features

- Tracks product availability and stock status
- Sends updates to a specified Telegram chat
- Flask server for keep-alive functionality

## Requirements

- Python 3.6+
- Telegram Bot API token
- Product API endpoint

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/sameterkanboz/product-tracker-bot.git
   cd product-tracker-bot
   ```

2. Create a virtual environment and activate it:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project directory and add your Telegram Bot token and chat ID:

   ```env
   TELEGRAM_TOKEN=your_telegram_token
   CHAT_ID=your_chat_id
   ```

## Usage

1. Run the Flask server to keep the bot alive:

   ```bash
   python main.py
   ```

2. The bot will start tracking the product and send updates to the specified Telegram chat.

## Functions

- `fetch_relevant_product_data(url)`: Fetches product data from the given URL.
- `send_product_data()`: Sends the fetched product data to the Telegram chat.
