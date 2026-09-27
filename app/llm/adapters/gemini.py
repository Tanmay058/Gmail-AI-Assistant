from langchain_google_genai import ChatGoogleGenerativeAI
from app.core import config
from .base import BaseLLMAdapter
import os

class GeminiAdapter(BaseLLMAdapter):
    def __init__(self):
        api_key = config.GOOGLE_API_KEY
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is missing. Please add it to your .env file.")
            
        print(f"[LLM FACTORY] Initializing Gemini Adapter with model: {config.GEMINI_MODEL}")
        self.llm = ChatGoogleGenerativeAI(
            model=config.GEMINI_MODEL,
            google_api_key=api_key,
            temperature=0,
            max_retries=0, # FAIL FAST if quota hit
            convert_system_message_to_human=True, 
            transport="rest" 
        )
    
    def invoke(self, input_data):
        return self.llm.invoke(input_data)
