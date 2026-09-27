import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("--- LISTING MODELS ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Found: {m.name}")
except Exception as e:
    print(f"List Error: {e}")

print("\n--- TESTING PREFERRED CANDIDATES ---")
candidates = [
    "gemini-2.0-flash-lite", 
    "gemini-2.0-flash-lite-preview-02-05", 
    "gemini-1.5-flash",
    "gemini-1.5-flash-001",
    "gemini-1.5-flash-002",
    "gemini-flash-lite", 
    "gemini-2.0-flash", # Known to have quota issues but let's see
]

for model_name in candidates:
    print(f"\nTrying: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hi", request_options={"timeout": 5})
        print(f"SUCCESS with {model_name}: {response.text}")
    except Exception as e:
        print(f"FAIL {model_name}: {e}")
