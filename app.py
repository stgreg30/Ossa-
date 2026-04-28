import os
import telebot
from flask import Flask, request
from core.brain_controller import executive_function 

# 1. Setup Flask for Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Ossa is Online and Conscious", 200

# 2. Setup Telegram Bot
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def chat(message):
    try:
        # This sends the message into the FULL Ossa cognitive cycle
        # It triggers: Perceive -> Feel -> Context -> Simulate -> Decide
        ossa_response = executive_function.pulse(message.text) 
        bot.reply_to(message, ossa_response)
    except Exception as e:
        # Sends the specific internal error to you on Telegram
        bot.reply_to(message, f"BRAIN ERROR: {str(e)}") 

# 3. Webhook Logic for Render Deployment
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/set_webhook")
def webhook():
    bot.remove_webhook()
    # Your specific Render URL
    bot.set_webhook(url=f'https://ossa-arjt.onrender.com/{TOKEN}')
    return "Webhook Set!", 200

if __name__ == "__main__":
    # [span_2](start_span)[span_3](start_span)INITIALIZE THE BRAIN: This loads identity.json and memories.json[span_2](end_span)[span_3](end_span)
    executive_function.initialize_brain() 
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
