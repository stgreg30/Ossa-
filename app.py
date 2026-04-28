import os
import telebot
from flask import Flask
import threading
import google.generativeai as genai

app = Flask(__name__)

@app.route('/')
def home():
    return "Ossa is Online", 200

# Setup Gemini - Using the most stable model name
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash') # Ensure this name is exact

bot = telebot.TeleBot(os.environ.get("TELEGRAM_BOT_TOKEN"))

@bot.message_handler(func=lambda message: True)
def chat(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        # This line will now show the real error in your Render Logs tab
        print(f"GEMINI ERROR: {e}") 
        bot.reply_to(message, "Ossa is having trouble thinking... check logs.")

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
