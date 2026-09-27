from langchain_ollama import OllamaLLM

llm = OllamaLLM(
    model="llama3.1:8b",
    temperature=0.1,
)

resp = llm.invoke(
    "Summarize: Please send invoice by Monday. It's urgent."
)

print(resp)

