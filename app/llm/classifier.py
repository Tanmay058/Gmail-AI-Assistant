from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from app.schemas.classification import ClassificationResult
import json
import re


llm = OllamaLLM(
    model="llama3.1:8b",
    temperature=0
)

prompt = PromptTemplate.from_template("""
You are a STRICT email classification API.

You MUST return ONLY valid JSON.
DO NOT add any explanation.
DO NOT add markdown.
DO NOT add text before or after JSON.

Schema:
{{
  "is_urgent": true or false,
  "is_spam": true or false,
  "sentiment": "positive" | "negative" | "neutral",
  "category": "invoice" | "meeting" | "support" | "sales" | "other"
}}

Email:
{email}
""")


def extract_json(text: str) -> dict:
    """
    Extract first JSON object from text safely.
    """
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise ValueError(f"No JSON found in LLM output:\n{text}")
    return json.loads(match.group())


def classify_email(email: str) -> ClassificationResult:
    chain = prompt | llm
    raw = chain.invoke({"email": email})

    print("\n----- RAW LLM OUTPUT -----")
    print(raw)
    print("--------------------------\n")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = extract_json(raw)

    return ClassificationResult(**data)

