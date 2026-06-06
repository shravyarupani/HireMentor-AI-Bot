# handlers/skills.py
# Handles /skills command — skill gap analysis

import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.gemini_service import analyze_skill_gap
from utils.formatters import split_message
from utils.keyboards import get_back_keyboard

logger = logging.getLogger(__name__)


async def skills_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Usage: /skills <current skills and target role>
    Example: /skills I know Python and SQL, I want to become an AI Engineer
    """
    if not context.args:
        await update.message.reply_text(
            "⚠️ *Please describe your skills and target role.*\n\n"
            "📝 *Usage:* `/skills <your skills + goal>`\n\n"
            "*Examples:*\n"
            "• `/skills I know Python and SQL, want to become a Data Scientist`\n"
            "• `/skills I know HTML and CSS, want to become a Full Stack Developer`\n"
            "• `/skills I have 2 years of Java experience, want to move into DevOps`",
            parse_mode="Markdown",
        )
        return

    user_message = " ".join(context.args).strip()
    logger.info(f"User {update.effective_user.id} requested skill gap analysis.")

    status_msg = await update.message.reply_text(
        "🔍 *Analysing your skill profile...*\n\n"
        "⏳ _Mapping gaps and building your action plan..._",
        parse_mode="Markdown",
    )

    try:
        result = await analyze_skill_gap(user_message)

        await status_msg.delete()

        header = (
            "🔍 *SKILL GAP ANALYSIS*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
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
        logger.error(f"Unexpected error in skills_handler: {e}")
        await status_msg.edit_text(
            "❌ An unexpected error occurred. Please try again.",
            parse_mode="Markdown",
        )
