from langchain_ollama import OllamaLLM


def get_llama_dev():
    return OllamaLLM(
        model="llama3.1:8b",
        temperature=0.1,
    )
