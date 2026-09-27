from langchain_ollama import OllamaLLM
from app.core import config
from .base import BaseLLMAdapter

class OllamaAdapter(BaseLLMAdapter):
    def __init__(self):
        print(f"[LLM FACTORY] Initializing Ollama Adapter with model: {config.OLLAMA_MODEL}")
        self.llm = OllamaLLM(
            model=config.OLLAMA_MODEL,
            temperature=0
        )
    
    def invoke(self, input_data):
        # Pass through to LangChain's invoke
        return self.llm.invoke(input_data)

    # Support the | operator for LangChain piping
    def __or__(self, other):
        return self.llm | other
    
    def __ror__(self, other):
        return other | self.llm
