import os
import telebot
from flask import Flask
import threading
from google import genai

app = Flask(__name__)

@app.route('/')
def home():
    return "Ossa is Online", 200

# Setup Gemini using the new SDK
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

bot = telebot.TeleBot(os.environ.get("TELEGRAM_BOT_TOKEN"))

@bot.message_handler(func=lambda message: True)
def chat(message):
    try:
        # The updated way to generate content
        response = client.models.generate_content(
            model='gemini-2.0-flash', 
            contents=message.text
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        # This line will show the real error in your Render Logs tab
        print(f"GEMINI ERROR: {e}") 
        bot.reply_to(message, "Ossa is having trouble thinking... check logs.")

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
