import os
from urllib.parse import urlparse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

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

# --- Authenticate ---
SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube"]

def build_youtube_client(token_path):
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    return build("youtube", "v3", credentials=creds)

youtube = build_youtube_client(TOKEN_FILE)

# --- Read description ---
with open(DESCRIPTION_FILE, "r", encoding="utf-8") as f:
    description = f.read()

# --- Extract headline from URL.txt ---
with open(URL_FILE, "r", encoding="utf-8") as f:
    url = f.read().strip()

parsed_url = urlparse(url)
path_parts = parsed_url.path.strip("/").split("/")
headline = path_parts[-2]  # SECOND-TO-LAST PART is the headline
TITLE = headline.replace("-", " ").capitalize()

def upload_video_and_thumbnail(youtube_client):
    # --- Upload video ---
    print("Uploading video...")
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
    print("Uploading thumbnail...")
    youtube_client.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(THUMBNAIL_FILE)
    ).execute()
    print("✅ Thumbnail uploaded successfully!")

try:
    upload_video_and_thumbnail(youtube)

except HttpError as e:
    error_str = str(e)
    if "uploadLimitExceeded" in error_str:
        print("⚠ Upload limit exceeded. Switching to fallback token...")
        try:
            youtube_fallback = build_youtube_client(FALLBACK_TOKEN_FILE)
            upload_video_and_thumbnail(youtube_fallback)
        except HttpError as fallback_error:
            print(f"Fallback upload also failed: {fallback_error}")
    else:
        print(f"An error occurred: {e}")