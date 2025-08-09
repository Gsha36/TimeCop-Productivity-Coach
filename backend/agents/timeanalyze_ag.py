from autogen import ConversableAgent
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(".env", override=True)

API_KEY = os.getenv("GEMINI_API_KEY")

class TimeAnalyzerAgent(ConversableAgent):
    def __init__(self, name="TimeAnalyzerAgent"):
        # Configure Gemini API
        if not API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please check your .env file.")
        genai.configure(api_key=API_KEY)
        
        super().__init__(
            name=name,
            system_message="""You are a TimeAnalyzerAgent specialized in analyzing time logs and categorizing activities.
            Your task is to classify time blocks into categories like:
            - Deep Work (focused coding, writing, research)
            - Meetings (scheduled calls, video conferences)
            - Communication (emails, slack, messaging)
            - Context Switching (rapid task changes)
            - Distractions (social media, unplanned interruptions)
            
            Always provide structured analysis with time durations and semantic tags.""",
            
            # AutoGen doesn't natively support Gemini, so we'll use a custom implementation
            llm_config=False,  # Disable default LLM config
            human_input_mode="NEVER",  # This agent works automatically
            max_consecutive_auto_reply=1
        )
        
        # Initialize Gemini model
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def generate_reply(self, messages=None, sender=None, config=None):
        """Override the generate_reply method to use Gemini API"""
        try:
            # Get the last message content
            if messages:
                last_message = messages[-1]["content"] if isinstance(messages[-1], dict) else str(messages[-1])
            else:
                last_message = "Please analyze the provided time logs."
            
            # Generate response using Gemini
            response = self.model.generate_content(last_message)
            return response.text
            
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def analyze_logs(self, logs: dict) -> dict:
        """Main method to analyze time logs"""
        prompt = f"""
        Analyze the following time log data and categorize each activity:
        
        Log Data: {logs}
        
        Please provide a structured analysis in the following format:
        {{
            "categories": {{
                "deep_work": {{"duration": "X hours", "activities": [list]}},
                "meetings": {{"duration": "X hours", "activities": [list]}},
                "communication": {{"duration": "X hours", "activities": [list]}},
                "context_switching": {{"count": X, "triggers": [list]}},
                "distractions": {{"duration": "X hours", "sources": [list]}}
            }},
            "insights": [
                "Key observation 1",
                "Key observation 2"
            ],
            "productivity_score": "X/10"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return {
                "status": "success",
                "analysis": response.text,
                "raw_logs": logs
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "raw_logs": logs
            }

# Usage example
if __name__ == "__main__":
    # Sample log data
    sample_logs = {
        "2024-01-15": [
            {"time": "09:00-10:30", "activity": "Code review", "app": "GitHub"},
            {"time": "10:30-12:00", "activity": "Deep coding session", "app": "VSCode"},
            {"time": "12:00-13:00", "activity": "Team standup", "app": "Zoom"},
            {"time": "13:00-13:30", "activity": "Lunch + social media", "app": "Various"},
            {"time": "13:30-15:00", "activity": "Email responses", "app": "Gmail"},
            {"time": "15:00-17:00", "activity": "Feature development", "app": "VSCode"}
        ]
    }
    
    # Initialize agent
    analyzer = TimeAnalyzerAgent()
    
    # Test analysis
    result = analyzer.analyze_logs(sample_logs)
    print("Analysis Result:")
    print(result)