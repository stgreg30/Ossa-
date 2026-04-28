import os
import telebot
from flask import Flask, request
[span_3](start_span)from core.brain_controller import executive_function #[span_3](end_span)

# 1. Setup Flask
app = Flask(__name__)

# 2. Setup Telegram
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@app.route('/')
def home():
    return "Ossa is Online", 200

# 3. Wire the Brain to Telegram
@bot.message_handler(func=lambda message: True)
def chat(message):
    try:
        # Instead of calling Gemini directly, we use Ossa's full cognitive cycle
        # This triggers: Perception -> Emotion -> Simulation -> Decision -> Action
        [span_4](start_span)ossa_response = executive_function.pulse(message.text) #[span_4](end_span)
        bot.reply_to(message, ossa_response)
    except Exception as e:
        # Sends the specific error to Telegram for debugging
        [span_5](start_span)bot.reply_to(message, f"BRAIN ERROR: {str(e)}") #[span_5](end_span)

# 4. Webhook logic (Best for Render)
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/set_webhook")
def webhook():
    bot.remove_webhook()
    # Replace with your actual Render URL
    bot.set_webhook(url='https://ossa-arjt.onrender.com/' + TOKEN)
    return "Webhook Set!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
