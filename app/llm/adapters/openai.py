# from langchain_openai import ChatOpenAI
# from app.core import config
from .base import BaseLLMAdapter

class OpenAIAdapter(BaseLLMAdapter):
    def __init__(self):
        # self.llm = ChatOpenAI(model=config.OPENAI_MODEL)
        raise NotImplementedError("OpenAI Adapter not fully configured within config.py yet.")
    
    def invoke(self, input_data):
        return self.llm.invoke(input_data)
        
    def __or__(self, other):
        return self.llm | other
    
    def __ror__(self, other):
        return other | self.llm
