# memory_ag.py

from autogen import ConversableAgent
import google.generativeai as genai
import os
from dotenv import load_dotenv
from backend.tools.vector_memory import store_summary, query_memory

# Load your Gemini key
load_dotenv(".env", override=True)
genai.configure(api_key="AIzaSyB3XnaVXMAzLgzG5TscSHbwlJt_BswvxY8")

class MemoryAgent(ConversableAgent):
    def __init__(self, name="MemoryAgent"):
        super().__init__(
            name=name,
            system_message="""
You are a MemoryAgent. Your job is to:
1. Take raw user activity logs.
2. Use Gemini to generate a concise 2-3 sentence summary (mood, energy, time, activity type).
3. Store that summary (plus raw log) into long-term memory for later retrieval.
""",
            llm_config=False,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1
        )
        # instantiate the Gemini model
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def generate_summary(self, raw_input: str) -> str:
        prompt = f"""
You are a productivity assistant. Summarize this activity log in 2-3 sentences,
highlighting mood, energy level, time mentions, and activity type.

Activity Log:
{raw_input}

Summary:
"""
        try:
            resp = self.model.generate_content(prompt)
            return resp.text.strip()
        except Exception as e:
            return f"[Summary generation failed] {e}"

    def remember(self, user_id: str, raw_input: str, summary_type: str = "voice_log"):
        """Summarize via Gemini and store the result."""
        summary = self.generate_summary(raw_input)
        store_summary(user_id, {
            "llm_summary": summary,
            "raw_input": raw_input
        }, summary_type=summary_type)
        return {
            "status": "stored",
            "user_id": user_id,
            "summary": summary
        }

    def recall(self, user_id: str, query: str = None, limit: int = 5) -> str:
        """Retrieve past summaries, optionally filtered by a keyword."""
        return query_memory(user_id, query=query, limit=limit)
