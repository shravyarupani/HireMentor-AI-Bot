# utils/formatters.py
# Helper utilities for formatting Telegram messages

import logging

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 4096  # Telegram's hard limit per message


def split_message(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> list[str]:
    """
    Split a long message into chunks that fit within Telegram's message limit.
    Tries to split on newlines to keep sections intact.
    """
    if len(text) <= max_length:
        return [text]

    chunks = []
    while len(text) > max_length:
        # Find the last newline within the allowed length
        split_index = text.rfind("\n", 0, max_length)
        if split_index == -1:
            # No newline found; hard-split at max_length
            split_index = max_length
        chunks.append(text[:split_index])
        text = text[split_index:].lstrip("\n")

    if text:
        chunks.append(text)

    return chunks


def escape_markdown(text: str) -> str:
    """
    Escape special MarkdownV2 characters so they render as plain text.
    Use only when inserting dynamic user-provided strings into MarkdownV2 messages.
    """
    special_chars = r"\_*[]()~`>#+-=|{}.!"
    for char in special_chars:
        text = text.replace(char, f"\\{char}")
    return text
