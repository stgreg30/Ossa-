import os
import telebot
from flask import Flask, request
from core.brain_controller import executive_function 

# 1. Setup Flask for Render health checks
app = Flask(__name__)

# 2. Setup Telegram Bot
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@app.route('/')
def home():
    return "Ossa is Online", 200

# 3. Connect the Telegram messages to Ossa's Brain
@bot.message_handler(func=lambda message: True)
def chat(message):
    try:
        # This sends the message into the full Ossa cognitive cycle
        ossa_response = executive_function.pulse(message.text) 
        bot.reply_to(message, ossa_response)
    except Exception as e:
        # This sends the error directly to you on Telegram if something breaks
        bot.reply_to(message, f"BRAIN ERROR: {str(e)}") 

# 4. Webhook logic for Render deployment
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/set_webhook")
def webhook():
    bot.remove_webhook()
    # Ensure this matches your Render service URL
    bot.set_webhook(url='https://ossa-arjt.onrender.com/' + TOKEN)
    return "Webhook Set!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
