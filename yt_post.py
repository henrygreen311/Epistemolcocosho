import os
from urllib.parse import urlparse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# --- Settings ---
TOKEN_FILE = "token.json"
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
creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
youtube = build("youtube", "v3", credentials=creds)

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

try:
    # --- Upload video ---
    print("Uploading video...")
    request = youtube.videos().insert(
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
    youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(THUMBNAIL_FILE)
    ).execute()
    print("✅ Thumbnail uploaded successfully!")

except HttpError as e:
    print(f"An error occurred: {e}")