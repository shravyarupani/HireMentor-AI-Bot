# handlers/linkedin.py
# Handles /linkedinpost command — generates a viral LinkedIn post

import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.gemini_service import generate_linkedin_post
from utils.formatters import split_message
from utils.keyboards import get_back_keyboard

logger = logging.getLogger(__name__)


async def linkedin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Usage: /linkedinpost <topic or achievement>
    Example: /linkedinpost Built an AI-powered Telegram bot using Gemini API
    """
    if not context.args:
        await update.message.reply_text(
            "⚠️ *Please provide a topic for your LinkedIn post.*\n\n"
            "📝 *Usage:* `/linkedinpost <topic>`\n\n"
            "*Examples:*\n"
            "• `/linkedinpost Got my AWS Solutions Architect certification`\n"
            "• `/linkedinpost Built an AI chatbot using Python and Gemini`\n"
            "• `/linkedinpost Started my first job as a data analyst`",
            parse_mode="Markdown",
        )
        return

    topic = " ".join(context.args).strip()
    logger.info(f"User {update.effective_user.id} requested LinkedIn post for: {topic}")

    status_msg = await update.message.reply_text(
        f"💼 *Crafting your LinkedIn post about:*\n`{topic}`\n\n"
        "⏳ _Writing a scroll-stopping post..._",
        parse_mode="Markdown",
    )

    try:
        result = await generate_linkedin_post(topic)

        await status_msg.delete()

        header = (
            "💼 *YOUR LINKEDIN POST*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "_Copy and paste this directly into LinkedIn_ 👇\n\n"
        )
        full_response = header + result
        chunks = split_message(full_response)

        for i, chunk in enumerate(chunks):
            reply_markup = get_back_keyboard() if i == len(chunks) - 1 else None
            await update.message.reply_text(
                chunk,
                parse_mode="Markdown",
                reply_markup=reply_markup,
            )

    except RuntimeError as e:
        await status_msg.edit_text(
            f"❌ *AI Service Error:* {e}\n\nPlease try again shortly.",
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Unexpected error in linkedin_handler: {e}")
        await status_msg.edit_text(
            "❌ An unexpected error occurred. Please try again.",
            parse_mode="Markdown",
        )
