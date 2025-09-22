from google.cloud import texttospeech
import os
import random
from google.api_core.exceptions import InvalidArgument

# --- Load Google service account key directly from same folder ---
key_path = os.path.join(os.path.dirname(__file__), "key.json")
client = texttospeech.TextToSpeechClient.from_service_account_file(key_path)

# --- Read input text from gemini.txt ---
with open("gemini.txt", "r", encoding="utf-8") as f:
    text_content = f.read()

# --- Voice pool (US, UK, Africa, India) ---
voice_pool = [
    # US voices
    {"language_code": "en-US", "name": "en-US-Wavenet-F"},  # Female US
    {"language_code": "en-US", "name": "en-US-Wavenet-D"},  # Male US

    # UK voices
    {"language_code": "en-GB", "name": "en-GB-Wavenet-A"},  # Male UK
    {"language_code": "en-GB", "name": "en-GB-Wavenet-C"},  # Female UK (fallback)

    # Africa (South Africa, English)
    {"language_code": "en-ZA", "name": "en-ZA-Wavenet-A"},  # Male Africa

    # India (English)
    {"language_code": "en-IN", "name": "en-IN-Wavenet-B"},  # Male India
]

# --- Randomly select one voice ---
selected_voice = random.choice(voice_pool)
print(f"🎤 Trying voice: {selected_voice['name']} ({selected_voice['language_code']})")

# --- Configure input ---
synthesis_input = texttospeech.SynthesisInput(text=text_content)

def synthesize(voice_choice):
    """Helper function to generate speech with given voice."""
    voice = texttospeech.VoiceSelectionParams(
        language_code=voice_choice["language_code"],
        name=voice_choice["name"]
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=0.85,  # slower for clarity
        pitch=0.0
    )
    return client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

try:
    # Try random voice
    response = synthesize(selected_voice)
except InvalidArgument:
    # Fallback to GB Female
    print("⚠️ Voice not available, falling back to en-GB-Wavenet-C (UK Female)")
    fallback_voice = {"language_code": "en-GB", "name": "en-GB-Wavenet-C"}
    response = synthesize(fallback_voice)

# --- Save to MP3 ---
with open("news_voice.mp3", "wb") as out:
    out.write(response.audio_content)

print("✅ News voice-over saved as news_voice.mp3")