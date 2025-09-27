import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# --- Settings ---
TOKEN_FILE = "token.json"           # Your OAuth token file
VIDEO_FILE = "news.mp4"             # Video to upload
THUMBNAIL_FILE = "preview.jpg"      # Thumbnail image
DESCRIPTION_FILE = "comment.txt"    # Video description
TITLE = "Automated News Upload"     # Video title
TAGS = ["news", "automation"]       # Video tags
CATEGORY_ID = "25"                  # News & Politics
PRIVACY_STATUS = "public"           # public/private/unlisted

# --- Authenticate with token.json ---
SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube"]

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
youtube = build("youtube", "v3", credentials=creds)

# --- Read video description ---
with open(DESCRIPTION_FILE, "r", encoding="utf-8") as f:
    description = f.read()

try:
    # --- Upload the video ---
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
            "status": {
                "privacyStatus": PRIVACY_STATUS
            }
        },
        media_body=MediaFileUpload(VIDEO_FILE)
    )
    response = request.execute()
    video_id = response["id"]
    print(f"✅ Video uploaded successfully! Video ID: {video_id}")

    # --- Set the thumbnail ---
    print("Uploading thumbnail...")
    youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(THUMBNAIL_FILE)
    ).execute()
    print("✅ Thumbnail uploaded successfully!")

except HttpError as e:
    print(f"An error occurred: {e}")