from autogen import ConversableAgent
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(".env", override=True)

API_KEY = os.getenv("GEMINI_API_KEY")

class InsightAgent(ConversableAgent):
    def __init__(self, name="InsightAgent"):
        if not API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please check your .env file.")
        genai.configure(api_key=API_KEY)
        super().__init__(
            name=name,
            system_message="""You are an InsightAgent specialized in finding patterns and anomalies in productivity data.
            Your responsibilities:
            - Analyze weekly work patterns
            - Identify productivity trends
            - Detect unusual activity patterns
            - Generate actionable insights
            - Provide data-driven observations
            
            Focus on meaningful patterns that can improve productivity.""",
            
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
                last_message = "Ready to analyze productivity data and generate insights."
            
            response = self.model.generate_content(last_message)
            return response.text
            
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def generate_insights(self, week_data: dict) -> dict:
        """Generate insights from weekly data"""
        prompt = f"""
        Analyze this weekly productivity data and generate key insights:
        
        Weekly Data: {week_data}
        
        Provide insights in this format:
        {{
            "key_patterns": [
                "Pattern 1: Description",
                "Pattern 2: Description"
            ],
            "anomalies": [
                "Anomaly 1: What was unusual",
                "Anomaly 2: What changed"
            ],
            "trends": {{
                "deep_work": "trend description",
                "meetings": "trend description",
                "productivity": "overall trend"
            }},
            "recommendations": [
                "Recommendation 1",
                "Recommendation 2"
            ]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return {
                "status": "success",
                "insights": response.text,
                "analyzed_period": week_data.get("period", "unknown")
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "analyzed_period": week_data.get("period", "unknown")
            }