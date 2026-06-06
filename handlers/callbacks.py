# handlers/callbacks.py
# Handles all InlineKeyboardButton callback queries from the main menu

import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils.keyboards import get_main_menu_keyboard, get_back_keyboard

logger = logging.getLogger(__name__)

# ── Instructional texts shown when user presses a menu button ─────────────────
MENU_RESPONSES = {
    "menu_resume": (
        "📄 *RESUME ANALYZER*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Simply *upload your PDF resume* to this chat and I'll instantly generate:\n\n"
        "• 📊 ATS Score (out of 100)\n"
        "• ✅ Key Strengths\n"
        "• ⚠️ Weaknesses & Gaps\n"
        "• 🔧 Missing Skills\n"
        "• 💡 Improvement Suggestions\n"
        "• 🎯 Suggested Job Roles\n\n"
        "_Just drag and drop your PDF into this chat!_ 👆"
    ),
    "menu_interview": (
        "🎤 *INTERVIEW PREP*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Get HR, technical & scenario questions for any role.\n\n"
        "📝 *Command:*\n"
        "`/interview <job role>`\n\n"
        "*Examples:*\n"
        "• `/interview software engineer`\n"
        "• `/interview data scientist`\n"
        "• `/interview product manager`\n"
        "• `/interview DevOps engineer`"
    ),
    "menu_roadmap": (
        "🗺️ *CAREER ROADMAP*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Get a complete, step-by-step learning path to your dream career.\n\n"
        "📝 *Command:*\n"
        "`/roadmap <target role>`\n\n"
        "*Examples:*\n"
        "• `/roadmap data analyst`\n"
        "• `/roadmap cloud architect`\n"
        "• `/roadmap AI engineer`\n"
        "• `/roadmap cybersecurity specialist`"
    ),
    "menu_skills": (
        "🔍 *SKILL GAP ANALYSIS*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Tell me your current skills and where you want to go — I'll map the gaps.\n\n"
        "📝 *Command:*\n"
        "`/skills <your skills + target role>`\n\n"
        "*Examples:*\n"
        "• `/skills I know Python and SQL, want to become ML Engineer`\n"
        "• `/skills I know HTML/CSS/JS, want to become Full Stack Dev`\n"
        "• `/skills I have an MBA, want to move into product management`"
    ),
    "menu_linkedin": (
        "💼 *LINKEDIN POST GENERATOR*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Generate a professional, viral LinkedIn post in seconds.\n\n"
        "📝 *Command:*\n"
        "`/linkedinpost <your topic or achievement>`\n\n"
        "*Examples:*\n"
        "• `/linkedinpost I got my first developer job`\n"
        "• `/linkedinpost Completed Google Data Analytics certification`\n"
        "• `/linkedinpost Launched my first SaaS product`"
    ),
    "menu_help": (
        "❓ *HELP & COMMANDS*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "*/start* — Welcome message & main menu\n"
        "*/interview [role]* — Interview prep questions\n"
        "*/roadmap [role]* — Career learning roadmap\n"
        "*/skills [skills + goal]* — Skill gap analysis\n"
        "*/linkedinpost [topic]* — LinkedIn post generator\n\n"
        "📄 *Resume Analysis* — Just upload a PDF file!\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 _All AI responses are powered by Google Gemini._\n"
        "🔒 _Your resume data is never stored._"
    ),
}


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route all inline keyboard button presses to the correct response."""
    query = update.callback_query
    await query.answer()  # Remove the loading spinner

    data = query.data
    logger.info(f"Callback received: {data} from user {update.effective_user.id}")

    if data == "menu_start":
        # Redirect back to welcome — import inline to avoid circular imports
        from handlers.start import WELCOME_MESSAGE
        user = update.effective_user
        first_name = user.first_name if user and user.first_name else "there"
        await query.edit_message_text(
            text=WELCOME_MESSAGE.format(name=first_name),
            parse_mode="Markdown",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    if data in MENU_RESPONSES:
        # All non-start menu items show instructions + a back button
        reply_markup = get_back_keyboard() if data != "menu_help" else get_main_menu_keyboard()
        await query.edit_message_text(
            text=MENU_RESPONSES[data],
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )
    else:
        await query.edit_message_text(
            "⚠️ Unknown action. Please use /start to go back to the menu.",
            parse_mode="Markdown",
            reply_markup=get_main_menu_keyboard(),
        )
