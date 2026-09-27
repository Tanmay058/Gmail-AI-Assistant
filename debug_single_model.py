import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model_name = "gemini-flash-lite-latest"
print(f"Testing {model_name}...")

try:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Hi", request_options={"timeout": 5})
    print(f"SUCCESS: {response.text}")
except Exception as e:
    print(f"FAIL: {e}")
