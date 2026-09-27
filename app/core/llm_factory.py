from app.core import config
import logging
from langchain_core.output_parsers import StrOutputParser

def get_llm():
    """
    Factory function to return the configured LLM Adapter.
    Uses app/llm/adapters/ for modularity.
    """
    provider = config.LLM_PROVIDER.lower()
    
    try:
        if provider == "ollama":
            from app.llm.adapters.ollama import OllamaAdapter
            return OllamaAdapter().llm
        
        elif provider == "openai":
            from app.llm.adapters.openai import OpenAIAdapter
            return OpenAIAdapter().llm | StrOutputParser()
            
        elif provider == "gemini":
            from app.llm.adapters.gemini import GeminiAdapter
            return GeminiAdapter().llm | StrOutputParser()
            
        # Add more providers here easily...
        
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
            
    except Exception as e:
        logging.error(f"Failed to initialize LLM provider '{provider}': {e}")
        # Fallback or re-raise?
        raise e
