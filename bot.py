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

    # ── Inline keyboard callback handler ──────────────────────────────────────
    app.add_handler(CallbackQueryHandler(callback_handler))

    logger.info("✅ All handlers registered successfully.")
    return app


def main() -> None:
    """Start the bot in polling mode with auto-retry on network failures."""
    logger.info("🚀 Starting AI Career Assistant Bot...")

    MAX_RETRIES = 10
    RETRY_DELAY = 5  # seconds between retries

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            app = build_application()
            logger.info(f"✅ Connected to Telegram API! (attempt {attempt})")

            # Run the bot until Ctrl-C is pressed
            app.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True,
            )
            break  # Clean exit (Ctrl+C)

        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user (Ctrl+C).")
            break

        except Exception as e:
            error_msg = str(e)
            if attempt < MAX_RETRIES:
                logger.warning(
                    f"⚠️  Network error on attempt {attempt}/{MAX_RETRIES}: {error_msg}\n"
                    f"    Retrying in {RETRY_DELAY} seconds..."
                )
                time.sleep(RETRY_DELAY)
            else:
                logger.error(
                    "❌ Failed to connect after %d attempts.\n"
                    "   Error: %s\n\n"
                    "💡 TROUBLESHOOTING:\n"
                    "   1. Check your internet connection\n"
                    "   2. Try changing DNS to 8.8.8.8 (Google) or 1.1.1.1 (Cloudflare)\n"
                    "   3. Try enabling/disabling a VPN\n"
                    "   4. Make sure no firewall is blocking api.telegram.org\n"
                    "   5. Verify your TELEGRAM_BOT_TOKEN in .env is correct",
                    MAX_RETRIES, error_msg,
                )
                raise


if __name__ == "__main__":
    main()
