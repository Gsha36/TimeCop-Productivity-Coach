from autogen import ConversableAgent
from backend.tools import google_calendar, github, gmail
import os
from dotenv import load_dotenv

load_dotenv(".env", override=True)

API_KEY = os.getenv("GEMINI_API_KEY")

class DataFetcherAgent(ConversableAgent):
    def __init__(self, name="DataFetcherAgent"):
        super().__init__(name=name)

    def fetch_all_logs(self, user_id: str) -> dict:
        return {
            "calendar": google_calendar.fetch_events(user_id),
            "github": github.fetch_activity(user_id),
            "email": gmail.fetch_email_metadata(user_id),
        }
