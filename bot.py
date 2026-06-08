# bot.py
# Entry point for the AI Career Assistant Telegram Bot
# Run: python bot.py

import logging
import os
import time
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

# ── Load environment variables from .env ──────────────────────────────────────
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ── Validate required environment variables ───────────────────────────────────
if not TELEGRAM_BOT_TOKEN:
    raise EnvironmentError("TELEGRAM_BOT_TOKEN is missing from the .env file.")
if not GEMINI_API_KEY:
    raise EnvironmentError("GEMINI_API_KEY is missing from the .env file.")

# ── Logging Configuration ─────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),                          # Console output
        logging.FileHandler("bot.log", encoding="utf-8"), # File output
    ],
)
logger = logging.getLogger(__name__)

# ── Import all feature handlers ───────────────────────────────────────────────
from handlers.start import start_handler, help_handler
from handlers.resume import resume_handler
from handlers.interview import interview_handler
from handlers.roadmap import roadmap_handler
from handlers.skills import skills_handler
from handlers.linkedin import linkedin_handler
from handlers.callbacks import callback_handler
from handlers.voice import voice_handler


def build_application() -> Application:
    """Build and configure the Telegram bot application with generous timeouts."""
    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .connect_timeout(30.0)      # seconds to wait for connection
        .read_timeout(30.0)         # seconds to wait for server response
        .write_timeout(30.0)        # seconds to wait when sending data
        .pool_timeout(30.0)         # seconds to wait for a connection from pool
        .build()
    )

    # ── Command handlers ──────────────────────────────────────────────────────
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("interview", interview_handler))
    app.add_handler(CommandHandler("roadmap", roadmap_handler))
    app.add_handler(CommandHandler("skills", skills_handler))
    app.add_handler(CommandHandler("linkedinpost", linkedin_handler))

    # ── Document handler (PDF resume upload) ──────────────────────────────────
    app.add_handler(MessageHandler(filters.Document.ALL, resume_handler))

    # ── Voice message handler ─────────────────────────────────────────────────
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))

    # ── Inline keyboard callback handler ──────────────────────────────────────
    app.add_handler(CallbackQueryHandler(callback_handler))

    logger.info("✅ All handlers registered successfully.")
    return app


import asyncio

async def run_bot() -> None:
    """Initialize and start the application loop cleanly."""
    app = build_application()
    
    # Initialize the application components (handlers, etc.)
    await app.initialize()
    
    # Start the network polling process
    await app.updater.start_polling(drop_pending_updates=True)
    
    # Start the runtime execution context
    await app.start()
    
    logger.info("🤖 Bot is now live and polling for updates...")
    
    # Keep running seamlessly until interrupted
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Shutting down bot processes...")
    finally:
        # Graceful cleanup layout
        if app.updater.running:
            await app.updater.stop()
        if app.running:
            await app.stop()
        await app.shutdown()


def main() -> None:
    """Main entry point configuration."""
    logger.info("🚀 Starting AI Career Assistant Bot...")
    try:
        # Explicitly run the main coroutine using modern asyncio handling
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user (Ctrl+C).")
    except Exception as e:
        logger.error(f"❌ Failed to run the application. Error: {str(e)}")
        raise


if __name__ == "__main__":
    main()