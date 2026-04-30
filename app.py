import os
import logging
from flask import Flask, request, abort
import telebot
from core.brain_controller import ExecutiveFunction

# Configure logging for better visibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the cognitive engine globally
executive_function = ExecutiveFunction()

# Telegram bot setup
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    raise EnvironmentError("TELEGRAM_BOT_TOKEN not set")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)

# Message handler (works in both modes)
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text
    logger.info(f"Received: {user_input}")
    try:
        response = executive_function.pulse(user_input)
        bot.reply_to(message, response)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        bot.reply_to(message, "I'm having a bit of trouble thinking right now. Please try again.")

# Health check / welcome
@bot.message_handler(commands=['start', 'init'])
def send_welcome(message):
    """Force a brain re‑initialisation if desired (only when webhook is active)"""
    executive_function.initialize_brain()
    bot.reply_to(message, "Ossa is awake and ready. You can start chatting!")

# ----------------- Webhook mode -----------------
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)

@app.route('/')
def index():
    return "Ossa is running."

# ----------------- Main entry point -----------------
if __name__ == '__main__':
    # Start the heartbeat / brain ONCE, now or later (if webhook, the /init route can also trigger it)
    executive_function.initialize_brain()

    mode = os.environ.get("MODE", "webhook").lower()

    if mode == "polling":
        logger.info("Starting Ossa in POLLING mode")
        # Polling blocks until stopped – no Flask needed
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    else:
        # Default: webhook mode (suitable for Render / production)
        logger.info("Starting Ossa in WEBHOOK mode")
        port = int(os.environ.get("PORT", 5000))
        app.run(host='0.0.0.0', port=port)