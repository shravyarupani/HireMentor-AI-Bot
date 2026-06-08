# handlers/roadmap.py
# Handles /roadmap command — generates career learning roadmap

import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.gemini_service import generate_career_roadmap
from utils.formatters import split_message
from utils.keyboards import get_back_keyboard

logger = logging.getLogger(__name__)


async def roadmap_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Usage: /roadmap <target role>
    Example: /roadmap data analyst
    """
    if not context.args:
        await update.message.reply_text(
            "⚠️ *Please specify a target role.*\n\n"
            "📝 *Usage:* `/roadmap <role>`\n\n"
            "*Examples:*\n"
            "• `/roadmap data analyst`\n"
            "• `/roadmap cloud engineer`\n"
            "• `/roadmap UI/UX designer`",
            parse_mode="Markdown",
        )
        return

    role = " ".join(context.args).strip()
    logger.info(f"User {update.effective_user.id} requested roadmap for: {role}")

    status_msg = await update.message.reply_text(
        f"🗺️ *Building career roadmap for:* `{role}`\n\n"
        "⏳ _Crafting your personalised learning path..._",
        parse_mode="Markdown",
    )

    try:
        result = await generate_career_roadmap(role)

        await status_msg.delete()

        header = (
            f"🗺️ *CAREER ROADMAP — {role.upper()}*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        )
        full_response = header + result
        chunks = split_message(full_response)

        for i, chunk in enumerate(chunks):
            reply_markup = get_back_keyboard() if i == len(chunks) - 1 else None
            await update.message.reply_text(
                chunk,
                reply_markup=reply_markup,
            )

    except RuntimeError as e:
        await status_msg.edit_text(
            f"❌ *AI Service Error:* {e}\n\nPlease try again shortly.",
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Unexpected error in roadmap_handler: {e}")
        await status_msg.edit_text(
            "❌ An unexpected error occurred. Please try again.",
            parse_mode="Markdown",
        )
