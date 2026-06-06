# services/pdf_service.py
# Handles PDF resume text extraction using pdfplumber (with PyPDF2 as fallback)

import logging
import io

import pdfplumber
import PyPDF2

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract plain text from a PDF given its raw bytes.
    Tries pdfplumber first (better accuracy), falls back to PyPDF2.

    Args:
        file_bytes: Raw bytes of the uploaded PDF file.

    Returns:
        Extracted text string. Raises ValueError if extraction fails.
    """
    text = ""

    # ── Attempt 1: pdfplumber ────────────────────────────────────────────────
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            logger.info("PDF extracted successfully via pdfplumber.")
            return text.strip()
    except Exception as e:
        logger.warning(f"pdfplumber failed: {e}. Falling back to PyPDF2.")

    # ── Attempt 2: PyPDF2 fallback ────────────────────────────────────────────
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        if text.strip():
            logger.info("PDF extracted successfully via PyPDF2.")
            return text.strip()
    except Exception as e:
        logger.error(f"PyPDF2 also failed: {e}")

    raise ValueError(
        "Could not extract text from the uploaded PDF. "
        "Please ensure it is a text-based (not scanned) PDF."
    )
