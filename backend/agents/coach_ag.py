from autogen import ConversableAgent
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(".env", override=True)

API_KEY = os.getenv("GEMINI_API_KEY")

class CoachAgent(ConversableAgent):
    def __init__(self, name="CoachAgent"):
        if not API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please check your .env file.")
        genai.configure(api_key=API_KEY)
        super().__init__(
            name=name,
            system_message="""You are a CoachAgent that provides personalized, motivating productivity advice.
            Your approach:
            - Use insights from data analysis
            - Reference user's historical patterns
            - Provide actionable, specific recommendations
            - Maintain an encouraging, supportive tone
            - Focus on sustainable productivity improvements
            
            Always personalize advice based on user's unique patterns and goals.""",
            
            llm_config=False,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1
        )
        
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def generate_reply(self, messages=None, sender=None, config=None):
        """Override the generate_reply method to use Gemini API"""
        try:
            if messages:
                last_message = messages[-1]["content"] if isinstance(messages[-1], dict) else str(messages[-1])
            else:
                last_message = "Ready to provide personalized productivity coaching."
            
            response = self.model.generate_content(last_message)
            return response.text
            
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def coach(self, insight_summary: str, user_history: str = None) -> dict:
        """Provide personalized coaching based on insights and history"""
        prompt = f"""
        Provide personalized productivity coaching based on:
        
        User History: {user_history or "No previous history available"}
        Current Week Insights: {insight_summary}
        
        Generate coaching advice in this format:
        {{
            "main_message": "Primary coaching message",
            "specific_tips": [
                "Tip 1: Specific actionable advice",
                "Tip 2: Another specific tip"
            ],
            "time_management": "Time management advice",
            "focus_strategies": "Focus improvement strategies",
            "motivation": "Motivational message",
            "next_week_goals": [
                "Goal 1",
                "Goal 2"
            ]
        }}
        
        Keep the tone encouraging and supportive while being specific and actionable.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return {
                "status": "success",
                "coaching": response.text,
                "based_on": insight_summary
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "based_on": insight_summary
            }