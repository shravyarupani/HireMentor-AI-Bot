# handlers/interview.py
# Handles /interview command — generates role-specific interview questions

import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.gemini_service import generate_interview_questions
from utils.formatters import split_message
from utils.keyboards import get_back_keyboard

logger = logging.getLogger(__name__)


async def interview_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Usage: /interview <role>
    Example: /interview data scientist
    """
    # ── Extract role from command args ────────────────────────────────────────
    if not context.args:
        await update.message.reply_text(
            "⚠️ *Please specify a job role.*\n\n"
            "📝 *Usage:* `/interview <role>`\n\n"
            "*Examples:*\n"
            "• `/interview frontend developer`\n"
            "• `/interview data scientist`\n"
            "• `/interview product manager`",
            parse_mode="Markdown",
        )
        return

    role = " ".join(context.args).strip()
    logger.info(f"User {update.effective_user.id} requested interview prep for: {role}")

    # ── Status message ────────────────────────────────────────────────────────
    status_msg = await update.message.reply_text(
        f"🎤 *Generating interview questions for:* `{role}`\n\n"
        "⏳ _Hang tight, preparing your personalised guide..._",
        parse_mode="Markdown",
    )

    try:
        result = await generate_interview_questions(role)

        await status_msg.delete()

        header = (
            f"🎤 *INTERVIEW PREP — {role.upper()}*\n"
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
        logger.error(f"Unexpected error in interview_handler: {e}")
        await status_msg.edit_text(
            "❌ An unexpected error occurred. Please try again.",
            parse_mode="Markdown",
        )
