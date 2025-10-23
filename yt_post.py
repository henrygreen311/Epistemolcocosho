import os
import re
from urllib.parse import urlparse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request  # For refresh support

# --- Settings ---
TOKEN_FILE = "token.json"
FALLBACK_TOKEN_FILE = "token_v2.json"
VIDEO_FILE = "news.mp4"
THUMBNAIL_FILE = "preview.jpg"
DESCRIPTION_FILE = "comment.txt"
URL_FILE = "URL.txt"
TAGS = ["news", "automation"]
CATEGORY_ID = "25"
PRIVACY_STATUS = "public"

# --- Scopes ---
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]


# --- Token management ---
def refresh_token_if_expired(token_path):
    """Load credentials and refresh if needed."""
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if creds.expired and creds.refresh_token:
        print(f"🔄 Token expired — refreshing {token_path} ...")
        creds.refresh(Request())
        with open(token_path, "w") as token:
            token.write(creds.to_json())
        print(f"✅ Token refreshed and saved for {token_path}.")
    return creds


def build_youtube_client(token_path):
    creds = refresh_token_if_expired(token_path)
    return build("youtube", "v3", credentials=creds)


# --- Initialize both tokens ---
youtube = build_youtube_client(TOKEN_FILE)
if os.path.exists(FALLBACK_TOKEN_FILE):
    refresh_token_if_expired(FALLBACK_TOKEN_FILE)


# --- Read description ---
with open(DESCRIPTION_FILE, "r", encoding="utf-8") as f:
    description = f.read()


# --- Extract title from URL ---
def extract_title_from_url(url):
    """
    Extract the slug between 'item/' and the next '/' before the token, 
    e.g.:
    https://www.reutersconnect.com/item/protesters-gather-in-madagascars-capital-after-rajoelina-cites-coup-plot/dGFn...
    -> protesters gather in madagascars capital after rajoelina cites coup plot
    """
    match = re.search(r"item/([^/]+)/", url)
    if match:
        slug = match.group(1)
        # Convert slug to readable title case
        return slug.replace("-", " ").title()
    else:
        # fallback: extract from URL path if regex fails
        parsed = urlparse(url)
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 2:
            slug = parts[-2]
            return slug.replace("-", " ").title()
        return "Untitled Upload"


# --- Read and derive title ---
with open(URL_FILE, "r", encoding="utf-8") as f:
    url = f.read().strip()
TITLE = extract_title_from_url(url)
print(f"📘 Extracted title: {TITLE}")


# --- Upload logic ---
def upload_video_and_thumbnail(youtube_client):
    print("📤 Uploading video...")
    request = youtube_client.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": TITLE,
                "description": description,
                "tags": TAGS,
                "categoryId": CATEGORY_ID
            },
            "status": {"privacyStatus": PRIVACY_STATUS}
        },
        media_body=MediaFileUpload(VIDEO_FILE)
    )

    response = request.execute()
    video_id = response["id"]
    print(f"✅ Video uploaded successfully! Video ID: {video_id}")

    # --- Upload thumbnail ---
    print("🖼️ Uploading thumbnail...")
    youtube_client.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(THUMBNAIL_FILE)
    ).execute()
    print("✅ Thumbnail uploaded successfully!")


# --- Main execution with fallback handling ---
try:
    upload_video_and_thumbnail(youtube)

except HttpError as e:
    error_str = str(e)
    if "uploadLimitExceeded" in error_str:
        print("⚠️ Upload limit exceeded. Switching to fallback token...")
        try:
            youtube_fallback = build_youtube_client(FALLBACK_TOKEN_FILE)
            upload_video_and_thumbnail(youtube_fallback)
        except HttpError as fallback_error:
            print(f"❌ Fallback upload also failed: {fallback_error}")
    else:
        print(f"❌ An error occurred: {e}")