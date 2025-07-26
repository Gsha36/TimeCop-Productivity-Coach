import json
import logging
import re
import textwrap
from typing import Dict
import random
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
import os
import openai
from faster_whisper import WhisperModel

logging.basicConfig(level=logging.DEBUG)

# Load your GEMINI API key from .env
load_dotenv(".env", override=True)
GEMINI_API_KEY = "AIzaSyB3XnaVXMAzLgzG5TscSHbwlJt_BswvxY8"

genai.configure(api_key=GEMINI_API_KEY)

model = WhisperModel("small", compute_type="float32")
# Instantiate the Gemini model for tagging
TAGGER_MODEL = genai.GenerativeModel('gemini-2.5-flash')

def transcribe_and_tag(audio_path: str) -> Dict:
    # 1️⃣ Transcribe
    segments, _ = model.transcribe(audio_path, beam_size=5)
    transcription = " ".join(seg.text for seg in segments).strip()
    logging.debug("🗣️ Transcription: %s", transcription)

    # 2️⃣ Build a “no fences” prompt
    system_prompt = textwrap.dedent("""\
        You MUST reply with exactly one plain JSON object, and nothing else.
        Do NOT wrap it in markdown, backticks, or any code fence.
        The object must have exactly these keys:
          mood           (positive|neutral|stressed|frustrated|excited|other)
          duration       (e.g. "30m","2h", or "unknown")
          activity_type  (deep_work|meetings|communication|distraction|collaboration|other)
          energy_level   (high|medium|low|unknown)
          confidence     (float 0.0-1.0)

        Example valid JSON (no fences):
        {"mood":"neutral","duration":"12h","activity_type":"deep_work","energy_level":"medium","confidence":0.85}
    """).strip()
    user_prompt = f"Transcript:\n\"\"\"\n{transcription}\n\"\"\""
    full_prompt = system_prompt + "\n\n" + user_prompt
    logging.debug("📝 Full Gemini prompt: %s", full_prompt)

    # 3️⃣ Call Gemini & strip any fences before parsing
    try:
        logging.debug("🔍 Calling Gemini...")
        resp = TAGGER_MODEL.generate_content(full_prompt)
        raw = resp.text.strip()
        logging.debug("📥 Gemini raw reply:\n%s", raw)

        # strip Markdown fences if present
        m = re.search(r"```(?:json)?\s*([\s\S]+?)```", raw)
        clean = m.group(1).strip() if m else raw

        logging.debug("🔧 After stripping fences:\n%s", clean)
        tags = json.loads(clean)
        logging.debug("✅ Parsed tags: %s", tags)

    except Exception as e:
        logging.error("❌ Tagging failed: %s", e, exc_info=True)
        if 'clean' in locals():
            logging.error("👀 Cleaned text was: %r", clean)
        tags = {
            "mood": "other",
            "duration": "unknown",
            "activity_type": "other",
            "energy_level": "unknown",
            "confidence": 0.0,
        }

    # 4️⃣ Return full result
    result = {
        "transcription": transcription,
        **tags,
        "timestamp": datetime.now().isoformat(),
        "audio_file": os.path.basename(audio_path),
    }
    logging.debug("▶️ Returning: %s", result)
    return result

    
def extract_activity_insights(transcription_result: Dict) -> Dict:
    """Extract additional insights from transcription for better analysis"""

    text = transcription_result["transcription"].lower()

    # (1) your existing bullet heuristics, if you still want them)
    # … productivity_indicators, time_mentions, emotional_keywords …

    # (2) Now build a prompt to get a 2–3 line AI summary:
    summary_system = """
    You are a helpful productivity coach. 
    Given a user's spoken log and its tags, provide a concise 2-3 sentence insight 
    highlighting what they did, their mood/energy, and one actionable suggestion.
    Respond *only* with the insight text (no bullets, no JSON).
    """
    tags = {
        k: transcription_result.get(k)
        for k in ("activity_type","mood","duration","energy_level")
    }
    summary_user = f"""
    Transcript: "{transcription_result['transcription']}"
    Tags: {json.dumps(tags)}
    """
    full_prompt = summary_system + "\n" + summary_user

    # Call Gemini for the summary
    try:
        summary_resp = genai.GenerativeModel("gemini-2.5-flash") \
                           .generate_content(full_prompt)
        insight_summary = summary_resp.text.strip()
    except Exception:
        insight_summary = "No additional insight available."

    # Return everything; replacing the old bullet dict if you like
    return {
        **transcription_result,
        "insight_summary": insight_summary,
        # optional: keep the old lists too
        # "insights": {
        #     "productivity_indicators": [...],
        #     "time_mentions": [...],
        #     "emotional_keywords": [...],
        #     "suggested_category": transcription_result.get("activity_type")
        # }
    }