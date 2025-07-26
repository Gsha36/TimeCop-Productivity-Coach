from autogen import ConversableAgent
import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv(".env", override=True)

API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini API globally
genai.configure(api_key=API_KEY)

class UserProxyAgent(ConversableAgent):
    def __init__(self, name="UserProxyAgent"):
        genai.configure(api_key="AIzaSyB3XnaVXMAzLgzG5TscSHbwlJt_BswvxY8")
        super().__init__(
            name=name,
            system_message="""You are a UserProxyAgent that interfaces with human users.
            Your task is to:
            - Receive and process user voice or text input
            - Convert user queries into structured formats
            - Handle user interactions professionally and helpfully
            - Route user requests to appropriate agents""",
            
            llm_config=False,  # Disable default LLM config
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1
        )
        
        # Initialize Gemini model
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def generate_reply(self, messages=None, sender=None, config=None):
        """Override the generate_reply method to use Gemini API"""
        try:
            if messages:
                last_message = messages[-1]["content"] if isinstance(messages[-1], dict) else str(messages[-1])
            else:
                last_message = "Hello! How can I help you with your productivity analysis today?"
            
            response = self.model.generate_content(last_message)
            return response.text
            
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def process_input(self, user_input: str) -> dict:
        """Process user input and structure it"""
        try:
            prompt = f"""
            Process this user input into a structured format:
            User Input: "{user_input}"
            
            Return a JSON structure with:
            {{
                "type": "user_query|voice_log|request",
                "content": "processed content",
                "intent": "what the user wants",
                "urgency": "low|medium|high"
            }}
            """
            
            response = self.model.generate_content(prompt)
            return {
                "status": "success",
                "processed_input": response.text,
                "original_input": user_input
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "original_input": user_input
            }