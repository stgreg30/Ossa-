import os
import telebot
from flask import Flask
import threading
import google.generativeai as genai

# 1. Setup Flask (for Render health checks)
app = Flask(__name__)

@app.route('/')
def home():
    return "Ossa is Online", 200

# 2. Setup Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

# 3. Setup Telegram
bot = telebot.TeleBot(os.environ.get("TELEGRAM_BOT_TOKEN"))

@bot.message_handler(func=lambda message: True)
def chat(message):
    try:
        # Send user message to Gemini
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "Ossa is having trouble thinking... check logs.")

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    # Start Telegram in the background
    threading.Thread(target=run_bot, daemon=True).start()
    # Start Flask on the port Render provides
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
