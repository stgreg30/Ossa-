"""
Ossa – Telegram Gateway (Flask + pyTelegramBotAPI)
=====================================================
Main entry point for the Ossa cognitive agent.
Supports both webhook (production) and polling (development) modes.
Provides health checks, brain initialisation, and debug state endpoints.
"""

import os
import sys
import signal
import logging
from typing import NoReturn

from flask import Flask, request, abort, jsonify
import telebot
from core.brain_controller import ExecutiveFunction

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ossa")

# ---------------------------------------------------------------------------
# Environment & Configuration
# ---------------------------------------------------------------------------
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    logger.critical("TELEGRAM_BOT_TOKEN environment variable not set.")
    sys.exit(1)

MODE = os.environ.get("MODE", "webhook").lower()
PORT = int(os.environ.get("PORT", 5000))

# ---------------------------------------------------------------------------
# Core Initialisation
# ---------------------------------------------------------------------------
logger.info("Initialising Ossa's cognitive engine...")
executive_function = ExecutiveFunction()

# Telegram Bot instance (non‑threaded, works with webhook)
bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)

# Flask Application
app = Flask(__name__)

# ---------------------------------------------------------------------------
# Telegram Message Handlers
# ---------------------------------------------------------------------------

@bot.message_handler(commands=['start', 'init'])
def handle_start(message: telebot.types.Message) -> None:
    """Initialise or re‑initialise the brain, then greet the user."""
    try:
        executive_function.initialize_brain()
        bot.reply_to(message, "Ossa is awake and ready. You can start chatting!")
    except Exception as e:
        logger.exception("Failed to initialise brain from /start")
        bot.reply_to(message, "I had trouble waking up. Please try again.")

@bot.message_handler(func=lambda message: True)
def handle_message(message: telebot.types.Message) -> None:
    """Process any incoming text message through the cognitive cycle."""
    user_input = message.text
    logger.info(f"Received: {user_input}")
    try:
        response = executive_function.pulse(user_input)
        bot.reply_to(message, response)
    except Exception as e:
        logger.exception("Error during cognitive cycle")
        bot.reply_to(message, "I'm having a bit of trouble thinking right now. Please try again.")

# ---------------------------------------------------------------------------
# Flask Webhook Route
# ---------------------------------------------------------------------------

@app.route('/webhook', methods=['POST'])
def webhook() -> tuple:
    """Receive Telegram updates via webhook."""
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        try:
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
        except Exception as e:
            logger.error(f"Failed to process update: {e}")
            abort(500)
        return '', 200
    else:
        abort(403)

# ---------------------------------------------------------------------------
# Health & Monitoring Endpoints
# ---------------------------------------------------------------------------

@app.route('/')
def index() -> str:
    """Basic liveness check (returns plain text)."""
    return "Ossa is running."

@app.route('/health')
def health() -> tuple:
    """Return JSON health status including brain and heartbeat states."""
    brain_ok = True  # if ExecutiveFunction exists
    heartbeat_running = executive_function.heartbeat._running if hasattr(executive_function.heartbeat, '_running') else False
    return jsonify({
        "status": "healthy",
        "brain_initialized": brain_ok,
        "heartbeat_running": heartbeat_running,
        "mode": MODE
    }), 200

@app.route('/init', methods=['GET'])
def init_brain() -> tuple:
    """Manually re‑initialise the brain and heartbeat."""
    try:
        executive_function.initialize_brain()
        return jsonify({"status": "initialized"}), 200
    except Exception as e:
        logger.exception("Brain init failed via API")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/set_webhook', methods=['POST'])
def set_webhook_endpoint() -> tuple:
    """Manually set or reset the Telegram webhook (useful for debugging)."""
    data = request.get_json(silent=True) or {}
    webhook_url = data.get('url') or request.host_url.rstrip('/') + '/webhook'
    try:
        result = bot.set_webhook(webhook_url)
        return jsonify({"status": "ok", "result": result, "url": webhook_url}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ---------------------------------------------------------------------------
# Debug State Endpoints (use with caution)
# ---------------------------------------------------------------------------

@app.route('/state/<key>')
def get_state(key: str) -> tuple:
    """Retrieve a state blob from the Thalamus (e.g., 'identity', 'beliefs', 'memories')."""
    try:
        data = executive_function.thalamus.get_state(key)
        return jsonify(data), 200
    except ValueError:
        return jsonify({"error": f"Unknown state key: {key}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/state/<key>', methods=['POST'])
def update_state(key: str) -> tuple:
    """Update a state blob (use with extreme caution)."""
    try:
        new_data = request.get_json(force=True)
        executive_function.thalamus.update_state(key, new_data)
        return jsonify({"status": "updated"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------------------------
# Graceful Shutdown
# ---------------------------------------------------------------------------

def shutdown_handler(signum, frame) -> NoReturn:
    """Stop the heartbeat and clean up before exiting."""
    logger.info("Shutdown signal received. Stopping heartbeat...")
    executive_function.heartbeat.stop()
    logger.info("Ossa shut down gracefully.")
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)

# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    # Start the background heartbeat (idempotent)
    try:
        executive_function.initialize_brain()
    except Exception as e:
        logger.error(f"Brain initialisation failed at startup: {e}")
        # Continue anyway; webhooks will start

    if MODE == "polling":
        logger.info("Starting Ossa in POLLING mode")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    else:
        logger.info(f"Starting Ossa in WEBHOOK mode on port {PORT}")
        # In production, consider using a WSGI server like gunicorn
        app.run(host='0.0.0.0', port=PORT)