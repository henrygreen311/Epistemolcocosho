import requests
import json
import re
import time

# --- Config ---
API_KEY = "AIzaSyCyvjN_7_kDRU8p0J3ANhbTpQwjcHrJ1gc"
MODEL = "gemini-2.0-flash"
OUTPUT_FILE = "gemini.txt"
URL_FILE = "URL.txt"

# --- Step 1: Read URL from file ---
with open(URL_FILE, "r", encoding="utf-8") as f:
    url_line = f.read().strip()

# --- Step 2: Extract the headline slug ---
match = re.search(r"/item/([^/]+)/", url_line)
if match:
    headline_slug = match.group(1).replace("-", " ")
else:
    raise ValueError("Could not extract headline slug from URL.txt")

# --- Step 3: Build prompt for Gemini ---
prompt = f"""
Rewrite the following headline into a professional, extended voice-over news script for video reporting.  
The script should be a single continuous paragraph, long enough to cover at least 30 seconds of narration.  
Include details such as escalation of conflict, humanitarian concerns, and broader regional implications.  
Credit VXN as the source.  
Also note that the footage was uploaded today, but avoid stage directions, URLs, or formatting.

At the end of the script, say: "Thank you for listening. Please follow or subscribe to get more updates from VXN News."

Headline: {headline_slug}
"""

# --- Step 4: Call Gemini API with retry ---
endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
headers = {"Content-Type": "application/json"}
data = {"contents": [{"parts": [{"text": prompt}]}]}

max_retries = 50
retry_delay = 20  # seconds

for attempt in range(1, max_retries + 1):
    response = requests.post(f"{endpoint}?key={API_KEY}", headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        try:
            result = response.json()
            text_output = result["candidates"][0]["content"]["parts"][0]["text"]
            print("✅ Success")
            break
        except (KeyError, IndexError):
            text_output = "Error: Could not parse Gemini response."
            break
    else:
        print(f"⚠️ Attempt {attempt} failed with {response.status_code}: {response.text}")
        if attempt < max_retries:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            continue
        else:
            text_output = f"Error {response.status_code}: {response.text}"
            break

# --- Step 5: Save to file ---
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(text_output)

print(f"News script saved to {OUTPUT_FILE}")