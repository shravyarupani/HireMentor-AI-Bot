# handlers/start.py
# Handles /start command and the welcome experience

import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils.keyboards import get_main_menu_keyboard

logger = logging.getLogger(__name__)

WELCOME_MESSAGE = """
🤖 *Welcome to AI Career Assistant!*
━━━━━━━━━━━━━━━━━━━━━━

Hey {name}! 👋 I'm your personal AI-powered career coach, here to supercharge your professional journey.

Here's what I can do for you:

📄 *Resume Analyzer* — Upload your PDF resume for an ATS score, strengths, weaknesses & job suggestions

🎤 *Interview Prep* — Get role-specific HR, technical & scenario questions
→ `/interview frontend developer`

🗺️ *Career Roadmap* — Get a complete skill & learning path to your dream role
→ `/roadmap data scientist`

🔍 *Skill Gap Analysis* — Tell me your skills & goal, I'll map the gaps
→ `/skills I know Python, want to become ML Engineer`

💼 *LinkedIn Post* — Generate a viral, professional LinkedIn post
→ `/linkedinpost I just completed my first ML project`

━━━━━━━━━━━━━━━━━━━━━━
*Choose a feature below or type a command to get started!* 🚀
"""


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the welcome message with the main menu keyboard."""
    user = update.effective_user
    first_name = user.first_name if user and user.first_name else "there"

    logger.info(f"User {user.id} ({first_name}) started the bot.")

    await update.message.reply_text(
        text=WELCOME_MESSAGE.format(name=first_name),
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard(),
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a detailed help/commands guide."""
    help_text = """
❓ *HELP — Available Commands*
━━━━━━━━━━━━━━━━━━━━━━

*/start* — Show welcome message & main menu

*/interview [role]* — Interview prep for any role
_Example:_ `/interview backend developer`

*/roadmap [role]* — Career roadmap for a target role
_Example:_ `/roadmap product manager`

*/skills [your skills + target role]* — Skill gap analysis
_Example:_ `/skills I know React and Node.js, want to become Full Stack Dev`

*/linkedinpost [topic]* — Generate a LinkedIn post
_Example:_ `/linkedinpost Got my AWS certification`

📄 *Resume Analysis* — Just send me your PDF resume file!

━━━━━━━━━━━━━━━━━━━━━━
💡 _Tip: Upload your PDF resume directly in the chat for a full analysis._
"""
    await update.message.reply_text(
        text=help_text,
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard(),
    )
