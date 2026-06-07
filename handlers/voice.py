# handlers/voice.py
# Handles voice messages — transcribes using Gemini multimodal and responds

import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.gemini_service import process_voice_message
from utils.formatters import split_message
from utils.keyboards import get_back_keyboard

logger = logging.getLogger(__name__)


async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Triggered when a user sends a voice message.
    Downloads the audio, sends to Gemini for transcription + AI response.
    """
    voice = update.message.voice
    if not voice:
        return

    # Keep status_msg alive — we only delete it AFTER confirming a response sent
    status_msg = await update.message.reply_text(
        "🎤 *Voice message received!*\n\n"
        "⏳ _Transcribing and analysing... this may take up to 30 seconds._",
        parse_mode="Markdown",
    )

    result = None
    try:
        # ── Download audio ─────────────────────────────────────────────────────
        file = await context.bot.get_file(voice.file_id)
        audio_bytes = await file.download_as_bytearray()

        logger.info(
            f"Voice from user {update.effective_user.id} — "
            f"{len(audio_bytes)} bytes, {voice.duration}s"
        )

        # ── Call Gemini multimodal ─────────────────────────────────────────────
        result = await process_voice_message(bytes(audio_bytes))

    except RuntimeError as e:
        await status_msg.edit_text(
            f"❌ *AI Error:*\n{e}\n\n_Please try again shortly._",
            parse_mode="Markdown",
        )
        return
    except Exception as e:
        logger.error(f"Voice handler error: {e}", exc_info=True)
        await status_msg.edit_text(
            "❌ Could not process your voice message.\nPlease try again.",
        )
        return

    # ── Send the response ──────────────────────────────────────────────────────
    header = (
        "🎤 *VOICE MESSAGE RESPONSE*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    full_response = header + result
    chunks = split_message(full_response)

    try:
        # Edit the status message with the first chunk (always safe — it exists)
        await status_msg.edit_text(
            chunks[0],
            parse_mode="Markdown",
            reply_markup=get_back_keyboard() if len(chunks) == 1 else None,
        )
    except Exception:
        # Markdown parse failed — retry as plain text
        try:
            await status_msg.edit_text(
                chunks[0],
                reply_markup=get_back_keyboard() if len(chunks) == 1 else None,
            )
        except Exception as e:
            logger.error(f"Could not edit status message: {e}")

    # Send any extra chunks as new messages
    for i, chunk in enumerate(chunks[1:], start=1):
        is_last = (i == len(chunks) - 1)
        try:
            await update.message.reply_text(
                chunk,
                parse_mode="Markdown",
                reply_markup=get_back_keyboard() if is_last else None,
            )
        except Exception:
            await update.message.reply_text(
                chunk,
                reply_markup=get_back_keyboard() if is_last else None,
            )

    logger.info(f"Voice response sent to user {update.effective_user.id}.")
