import os
import logging
from flask import Flask, request, abort
import telebot
from core.brain_controller import ExecutiveFunction

# Initialize the cognitive engine globally
executive_function = ExecutiveFunction()

app = Flask(__name__)

# Telegram bot setup
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    raise EnvironmentError("TELEGRAM_BOT_TOKEN not set")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)

# Webhook route
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)

# Message handler
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text
    logging.info(f"Received: {user_input}")
    # Run through Ossa's cognitive cycle
    response = executive_function.pulse(user_input)
    bot.reply_to(message, response)

# Initialization endpoint (optional)
@app.route('/init', methods=['GET'])
def init_brain():
    executive_function.initialize_brain()
    return "Brain initialized and heartbeat started."

# Health check
@app.route('/')
def index():
    return "Ossa is running."

if __name__ == '__main__':
    # Start the heartbeat when the app starts
    executive_function.initialize_brain()
    # Run Flask
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)