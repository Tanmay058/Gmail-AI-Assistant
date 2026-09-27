
import os
import socket
import requests
from dotenv import load_dotenv

load_dotenv()

def check_host(host, port=443):
    try:
        socket.create_connection((host, port), timeout=5)
        print(f"[OK] Reached {host}:{port}")
        return True
    except OSError as e:
        print(f"[ERROR] Cannot reach {host}:{port} - {e}")
        return False

def test_api_call(name, url, headers=None):
    try:
        response = requests.get(url, headers=headers, timeout=5)
        print(f"[{name}] Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"[{name}] Connection Failed: {e}")
        return False

print("--- Network Diagnosis ---")

# 1. Check DNS / Basic Internet
check_host("8.8.8.8", 53)
check_host("google.com", 443)

# 2. Check Gemini API
print("\n--- Testing Gemini API ---")
check_host("generativelanguage.googleapis.com", 443)

# 3. Check Supabase
supabase_url = os.environ.get("SUPABASE_URL")
if supabase_url:
    host = supabase_url.replace("https://", "").split("/")[0]
    print(f"\n--- Testing Supabase ({host}) ---")
    check_host(host, 443)
else:
    print("\n[SKIP] Supabase URL not found in .env")

# 4. Check Gmail API
print("\n--- Testing Gmail API ---")
check_host("www.googleapis.com", 443)

print("\n--- Diagnosis Complete ---")

