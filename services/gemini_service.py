# services/gemini_service.py
# All Gemini AI API interactions using the official google-genai SDK

import asyncio
import logging
import os

from google import genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# ── Gemini Client Setup ───────────────────────────────────────────────────────
_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Model fallback chain — tries each model until one works
MODELS = [
    "gemini-2.5-flash",        # ✅ confirmed working
    "gemini-flash-latest",     # alias fallback
    "gemini-2.5-flash-lite",   # lighter fallback
    "gemini-2.0-flash",        # last resort
]


async def _call_with_retry(fn, model_name: str, max_retries: int = 2) -> str:
    """
    Call a Gemini function with exponential backoff retry for 503 errors.
    Retries up to max_retries times with 2s, 4s delays.
    Kept short so the user doesn't wait too long.
    """
    for attempt in range(1, max_retries + 1):
        try:
            return await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, fn),
                timeout=90.0,
            )
        except asyncio.TimeoutError:
            raise  # bubble up — caller handles it
        except Exception as e:
            err_str = str(e)
            is_503 = "503" in err_str or "UNAVAILABLE" in err_str or "high demand" in err_str.lower()
            if is_503 and attempt < max_retries:
                wait = 2 * attempt  # 2s, 4s
                logger.warning(
                    f"⏳ {model_name} overloaded (503). "
                    f"Retrying in {wait}s... ({attempt}/{max_retries})"
                )
                await asyncio.sleep(wait)
                continue
            raise  # not 503, or retries exhausted


async def call_gemini(prompt: str) -> str:
    """
    Send a prompt to Gemini and return the text response.
    Tries multiple models in order. Retries on 503 with exponential backoff.
    Thinking mode is disabled for fast responses.
    """
    from google.genai import types

    last_error = None

    for model_name in MODELS:
        try:
            logger.info(f"Calling Gemini model: {model_name}")

            def _generate():
                config = types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                )
                try:
                    response = _client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=config,
                    )
                except Exception:
                    response = _client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                return response.text.strip()

            result = await _call_with_retry(_generate, model_name)
            logger.info(f"✅ Gemini responded using {model_name}")
            return result

        except asyncio.TimeoutError:
            logger.warning(f"⏱ {model_name} timed out. Trying next model...")
            last_error = "Request timed out."
            continue
        except Exception as e:
            err_str = str(e)
            if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str or "quota" in err_str.lower():
                logger.warning(f"⚠ Quota exhausted for {model_name}. Trying next model...")
                last_error = err_str
                continue
            elif "not found" in err_str.lower() or "404" in err_str:
                logger.warning(f"⚠ Model {model_name} not found. Trying next model...")
                last_error = err_str
                continue
            elif "503" in err_str or "UNAVAILABLE" in err_str:
                logger.warning(f"⚠ {model_name} still unavailable after retries. Trying next model...")
                last_error = err_str
                continue
            else:
                logger.error(f"Gemini API error with {model_name}: {e}")
                raise RuntimeError(f"Gemini API error: {e}")

    raise RuntimeError(
        "All Gemini models are currently unavailable or quota is exhausted.\n"
        "Please try again in a few minutes."
    )


# ─────────────────────────────────────────────────────────────────────────────
#  FEATURE PROMPTS
# ─────────────────────────────────────────────────────────────────────────────

async def analyze_resume(resume_text: str) -> str:
    """Generate a comprehensive ATS-style resume analysis."""
    prompt = f"""
You are an expert career coach and ATS (Applicant Tracking System) specialist.
Analyze the following resume and provide a detailed, professional report.

RESUME TEXT:
\"\"\"
{resume_text}
\"\"\"

Please provide your analysis in the following structured format using emojis and clear sections:

📊 ATS SCORE
Give a score out of 100 and a one-line verdict.

✅ KEY STRENGTHS
List 4–5 strong points found in the resume as bullet points.

⚠️ WEAKNESSES & GAPS
List 4–5 areas that need improvement as bullet points.

🔧 MISSING SKILLS
List specific technical or soft skills that are absent but recommended.

💡 IMPROVEMENT SUGGESTIONS
Provide 5 actionable, specific suggestions to improve this resume.

🎯 SUGGESTED JOB ROLES
List 5 job roles this candidate is well-suited for, with a brief reason for each.

Format everything cleanly for a Telegram message. Use emojis, bullet points (•), and section dividers (───).
Keep the language professional, encouraging, and constructive.
"""
    return await call_gemini(prompt)


async def generate_interview_questions(role: str) -> str:
    """Generate categorised interview questions for a given job role."""
    prompt = f"""
You are a senior hiring manager and career coach.
Generate a comprehensive interview preparation guide for the role: {role}

Structure your response with the following sections:

HR / BEHAVIORAL QUESTIONS
List 5 common HR questions with brief tips on how to answer each.

TECHNICAL QUESTIONS
List 6 role-specific technical questions (with expected answer hints).

SCENARIO-BASED QUESTIONS
List 4 real-world scenario questions that test problem-solving skills.

PRO TIPS FOR THE INTERVIEW
Provide 5 actionable tips to ace this interview.

Format for Telegram: use emojis, bullet points, and section dividers.
Keep it practical and confidence-building.
"""
    return await call_gemini(prompt)


async def generate_career_roadmap(role: str) -> str:
    """Generate a step-by-step career roadmap for a target role."""
    prompt = f"""
You are an expert career strategist and industry mentor.
Create a detailed, actionable career roadmap to become a: {role}

Include the following sections:

CAREER ROADMAP OVERVIEW
A 2-3 sentence summary of the path.

REQUIRED SKILLS
Categorised list: Core Skills | Advanced Skills | Soft Skills

TOOLS & TECHNOLOGIES
Essential tools, platforms, and software to learn.

LEARNING RESOURCES
Top 3-5 free and paid resources (courses, books, channels).

PROJECTS TO BUILD
5 portfolio projects that will impress employers.

CERTIFICATIONS
Top 3-5 certifications that add credibility.

LEARNING TIMELINE
Break the journey into phases:
• Phase 1 (0-3 months): Foundations
• Phase 2 (3-6 months): Core Skills
• Phase 3 (6-12 months): Advanced & Job-Ready

Format for Telegram: use emojis, bullet points, and section dividers.
Be specific, motivating, and realistic.
"""
    return await call_gemini(prompt)


async def analyze_skill_gap(user_message: str) -> str:
    """Perform a skill gap analysis based on the user's current skills and target role."""
    prompt = f"""
You are a professional career advisor and skills coach.
Based on the following user message, perform a detailed skill gap analysis.

USER MESSAGE:
"{user_message}"

Provide your analysis in these sections:

SKILL GAP ANALYSIS SUMMARY
Brief summary of what the user has vs. what they need.

SKILLS YOU ALREADY HAVE
List the relevant skills identified in the user's message.

MISSING CRITICAL SKILLS
List skills that are absolutely required for the target role but absent.

SKILLS TO LEVEL UP
List skills the user may have at a basic level but need to deepen.

LEARNING RECOMMENDATIONS
For each missing skill, suggest a free and a paid learning resource.

PROJECT IDEAS
Suggest 4 hands-on projects that will close the skill gap and build a portfolio.

ESTIMATED TIME TO TRANSITION
Give a realistic timeline estimate with monthly milestones.

Format for Telegram: use emojis, bullet points, and section dividers.
Be encouraging, specific, and actionable.
"""
    return await call_gemini(prompt)


async def process_voice_message(audio_bytes: bytes) -> str:
    """
    Transcribe a Telegram voice message (OGG format) and generate
    a career-assistant response using Gemini's multimodal capability.
    """
    from google.genai import types

    loop = asyncio.get_event_loop()

    for model_name in MODELS:
        try:
            logger.info(f"Processing voice with {model_name}")

            def _process():
                response = _client.models.generate_content(
                    model=model_name,
                    contents=[
                        types.Part.from_bytes(
                            data=audio_bytes,
                            mime_type="audio/ogg",
                        ),
                        (
                            "You are an AI Career Assistant. "
                            "First, transcribe what the user said in this voice message. "
                            "Then respond as a professional career coach. "
                            "If it's a career question (resume, interview, skills, roadmap, LinkedIn), "
                            "give a detailed, helpful answer. "
                            "If it's a general greeting, respond warmly and list what you can help with.\n\n"
                            "Format your response for Telegram:\n"
                            "\U0001f399\ufe0f *What you said:* <transcription here>\n\n"
                            "\U0001f4ac *My response:* <career advice here>"
                        ),
                    ],
                )
                return response.text.strip()

            result = await _call_with_retry(_process, model_name)
            logger.info(f"\u2705 Voice processed using {model_name}")
            return result

        except asyncio.TimeoutError:
            logger.warning(f"\u23f1 Voice timed out for {model_name}. Trying next...")
            continue
        except Exception as e:
            err_str = str(e)
            if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str or "quota" in err_str.lower():
                logger.warning(f"\u26a0 Quota issue for {model_name}, trying next...")
                continue
            elif "not found" in err_str.lower() or "404" in err_str:
                logger.warning(f"\u26a0 Model {model_name} not found, trying next...")
                continue
            elif "503" in err_str or "UNAVAILABLE" in err_str:
                logger.warning(f"\u26a0 {model_name} still unavailable after retries. Trying next...")
                continue
            else:
                logger.error(f"Voice processing error: {e}")
                raise RuntimeError(f"Could not process voice message: {e}")

    raise RuntimeError(
        "The AI is currently busy. Please send your voice message again in a moment."
    )


async def generate_linkedin_post(topic: str) -> str:
    """Generate a professional, engaging LinkedIn post for a given topic."""
    prompt = f"""
You are a top LinkedIn content creator and personal branding expert.
Write a viral, professional LinkedIn post about: {topic}

The post MUST include:

ENGAGING HOOK (first line)
A powerful opening line that stops the scroll. No cliches.

STORY / BODY
3-5 short paragraphs with personal insight, lessons learned, or a narrative.
Use line breaks generously for readability.

KEY TAKEAWAYS
3-5 bullet points with actionable lessons or insights.

CALL TO ACTION
End with a question or prompt that encourages comments and engagement.

HASHTAGS
10-15 relevant, trending hashtags.

Guidelines:
• Keep sentences short and punchy.
• Use emojis naturally within the text.
• Professional yet conversational tone.
• Total length: 150-250 words (not counting hashtags).

Return ONLY the post content, ready to copy-paste into LinkedIn.
"""
    return await call_gemini(prompt)
