# utils/keyboards.py
# Inline keyboard button layouts for the bot

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Returns the main menu inline keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("📄 Resume Analysis", callback_data="menu_resume"),
            InlineKeyboardButton("🎤 Interview Prep", callback_data="menu_interview"),
        ],
        [
            InlineKeyboardButton("🗺️ Career Roadmap", callback_data="menu_roadmap"),
            InlineKeyboardButton("🔍 Skill Gap Analysis", callback_data="menu_skills"),
        ],
        [
            InlineKeyboardButton("💼 LinkedIn Post", callback_data="menu_linkedin"),
            InlineKeyboardButton("❓ Help", callback_data="menu_help"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Returns a simple 'Back to Menu' button."""
    keyboard = [
        [InlineKeyboardButton("🏠 Back to Main Menu", callback_data="menu_start")]
    ]
    return InlineKeyboardMarkup(keyboard)
