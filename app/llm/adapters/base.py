from abc import ABC, abstractmethod

class BaseLLMAdapter(ABC):
    """
    Interface for all LLM adapters.
    Ensures consistent behavior across different providers (Ollama, OpenAI, Vertex, etc.)
    """
    
    @abstractmethod
    def invoke(self, prompt: str) -> str:
        """
        Send a prompt to the LLM and return the text response.
        Should handle its own error catching/retries if needed.
        """
        pass
    
    # Ideally we'd support LangChain's Runnable interface for piping
    # For now, we wrap the underlying LangChain object or raw API
