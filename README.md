# AI Career Assistant — Telegram Bot

> 🤖 A fully AI-powered Telegram chatbot for career growth — built with Python, Gemini AI, and python-telegram-bot.

---

## ✨ Features

| Feature | Command | Description |
|---|---|---|
| 📄 Resume Analyzer | Upload PDF | ATS score, strengths, weaknesses, job suggestions |
| 🎤 Interview Prep | `/interview <role>` | HR, technical & scenario-based questions |
| 🗺️ Career Roadmap | `/roadmap <role>` | Skills, tools, projects, certifications & timeline |
| 🔍 Skill Gap Analysis | `/skills <skills + goal>` | Gap mapping + learning recommendations |
| 💼 LinkedIn Post | `/linkedinpost <topic>` | Viral, professional LinkedIn post generator |
| ❓ Help | `/help` | Full command reference |

---

## 🗂️ Project Structure

```
ai_resume/
├── bot.py                  # Main entry point
├── requirements.txt        # Python dependencies
├── render.yaml             # Render.com deployment config
├── .env                    # API keys (never commit this!)
├── bot.log                 # Auto-generated log file
│
├── handlers/               # Telegram command & event handlers
│   ├── __init__.py
│   ├── start.py            # /start, /help
│   ├── resume.py           # PDF upload → resume analysis
│   ├── interview.py        # /interview
│   ├── roadmap.py          # /roadmap
│   ├── skills.py           # /skills
│   ├── linkedin.py         # /linkedinpost
│   └── callbacks.py        # Inline keyboard callbacks
│
├── services/               # Business logic & external APIs
│   ├── __init__.py
│   ├── gemini_service.py   # All Gemini AI prompt calls
│   └── pdf_service.py      # PDF text extraction
│
└── utils/                  # Shared utilities
    ├── __init__.py
    ├── keyboards.py        # Inline keyboard layouts
    └── formatters.py       # Message splitting & formatting
```

---

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.10+
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- A Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/)

### 2. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-career-assistant-bot.git
cd ai-career-assistant-bot
```

### 3. Create a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Create a `.env` file in the project root (already exists if you cloned):
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
```

> ⚠️ **Never commit your `.env` file to Git!** Add it to `.gitignore`.

### 6. Run the Bot Locally
```bash
python bot.py
```

You should see:
```
✅ All handlers registered successfully.
🚀 Starting AI Career Assistant Bot...
```

---

## 🤖 Bot Commands Reference

| Command | Example | What it does |
|---|---|---|
| `/start` | `/start` | Welcome message + main menu |
| `/help` | `/help` | All commands explained |
| `/interview` | `/interview data scientist` | Generate interview questions |
| `/roadmap` | `/roadmap cloud engineer` | Full career roadmap |
| `/skills` | `/skills I know Python, want ML job` | Skill gap analysis |
| `/linkedinpost` | `/linkedinpost Got AWS certified` | LinkedIn post generator |
| *(send PDF)* | Upload resume.pdf | Full resume ATS analysis |

---

## 🚀 Deploy on Render

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/ai-career-assistant-bot.git
git push -u origin main
```

> ⚠️ Make sure `.env` is in your `.gitignore` before pushing!

### Step 2 — Create New Service on Render
1. Go to [render.com](https://render.com) and log in.
2. Click **New → Background Worker**.
3. Connect your GitHub repository.
4. Render will auto-detect `render.yaml`.

### Step 3 — Set Environment Variables
In the Render dashboard → your service → **Environment**:
- Add `TELEGRAM_BOT_TOKEN` = your token
- Add `GEMINI_API_KEY` = your API key

### Step 4 — Deploy
Click **Manual Deploy → Deploy Latest Commit**. Your bot will go live! 🎉

---

## 🔐 Security Notes

- API keys are loaded from `.env` using `python-dotenv` — never hardcoded.
- Resume PDFs are processed in-memory and **never saved to disk**.
- Add `.env` and `bot.log` to your `.gitignore`.

### Recommended `.gitignore`
```
.env
venv/
__pycache__/
*.pyc
bot.log
*.pdf
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core language |
| python-telegram-bot 21.x | Telegram Bot API wrapper |
| Google Gemini 1.5 Flash | AI content generation |
| pdfplumber | Primary PDF text extraction |
| PyPDF2 | Fallback PDF extraction |
| python-dotenv | Secure environment variable loading |

---

## 📸 Screenshots

> *(Add screenshots of your bot here)*

| Welcome Screen | Resume Analysis | Interview Prep |
|---|---|---|
| ![welcome](screenshots/welcome.png) | ![resume](screenshots/resume.png) | ![interview](screenshots/interview.png) |

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## 📄 License

MIT License — free to use, modify and distribute.

---

*Built with ❤️ using Python + Gemini AI*
