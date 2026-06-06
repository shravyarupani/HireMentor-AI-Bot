# handlers/resume.py
# Handles PDF resume upload → extraction → Gemini analysis

import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.pdf_service import extract_text_from_pdf
from services.gemini_service import analyze_resume
from utils.formatters import split_message
from utils.keyboards import get_back_keyboard

logger = logging.getLogger(__name__)


async def resume_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Triggered when a user uploads a document.
    Only processes PDF files; ignores other document types.
    """
    document = update.message.document

    # ── Guard: only handle PDFs ───────────────────────────────────────────────
    if not document or document.mime_type != "application/pdf":
        await update.message.reply_text(
            "⚠️ Please upload a *PDF* file for resume analysis.\n"
            "_Other file types are not supported._",
            parse_mode="Markdown",
        )
        return

    # ── Acknowledge receipt ───────────────────────────────────────────────────
    status_msg = await update.message.reply_text(
        "📄 *Resume received!*\n\n"
        "⏳ Extracting text and running AI analysis...\n"
        "_This may take 15–30 seconds._",
        parse_mode="Markdown",
    )

    try:
        # ── Download PDF bytes ────────────────────────────────────────────────
        file = await context.bot.get_file(document.file_id)
        file_bytes = await file.download_as_bytearray()

        # ── Extract text ──────────────────────────────────────────────────────
        resume_text = extract_text_from_pdf(bytes(file_bytes))

        if len(resume_text.strip()) < 100:
            await status_msg.edit_text(
                "❌ *Could not extract enough text from the PDF.*\n\n"
                "Please make sure your resume is a *text-based PDF* "
                "(not a scanned image). Try saving it as PDF from Word or Google Docs.",
                parse_mode="Markdown",
            )
            return

        logger.info(f"Extracted {len(resume_text)} characters from resume.")

        # ── Call Gemini ───────────────────────────────────────────────────────
        analysis = await analyze_resume(resume_text)

        # ── Delete status message & send analysis ─────────────────────────────
        await status_msg.delete()

        header = (
            "✅ *RESUME ANALYSIS COMPLETE*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        )
        full_response = header + analysis

        # Split if response is too long for one Telegram message
        chunks = split_message(full_response)
        for i, chunk in enumerate(chunks):
            reply_markup = get_back_keyboard() if i == len(chunks) - 1 else None
            await update.message.reply_text(
                chunk,
                parse_mode="Markdown",
                reply_markup=reply_markup,
            )

        logger.info(f"Resume analysis sent to user {update.effective_user.id}.")

    except ValueError as e:
        # PDF extraction error
        await status_msg.edit_text(
            f"❌ *PDF Error:* {e}",
            parse_mode="Markdown",
        )
    except RuntimeError as e:
        # Gemini API error
        await status_msg.edit_text(
            f"❌ *AI Service Error:* {e}\n\nPlease try again in a moment.",
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Unexpected error in resume_handler: {e}")
        await status_msg.edit_text(
            "❌ An unexpected error occurred. Please try again.",
            parse_mode="Markdown",
        )
