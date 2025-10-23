import subprocess
import requests
import os
import re

PAGE_ID = "796052743592190"
ACCESS_TOKEN = "EAAVQdbJuFuMBPhlAaQJ44KnO6yxEwJ6bCRz9C3QjLahsgkhs6zqTYOO7RWkmxghvNXWMc0J5RhpCcCh7FrpBWtjm3P92QbWvBJgCOfatFziynFIIEZBNPZBSMEUbQLf8S3HO34kEpVlIdWD5rInMkvVklhznzwoMyZAMsspQYGL0umfCMa2l7c9gGKwaNeiq0QZAOKIb"

FULL_VIDEO = "news.mp4"
COMMENT_FILE = "comment.txt"
PREVIEW_IMAGE = "preview.jpg"
URL_FILE = "URL.txt"


def extract_title_from_url(url_path):
    """Extract the slug between 'item/' and the next '/' before the token."""
    match = re.search(r"item/([^/]+)/", url_path)
    if match:
        return match.group(1).replace("-", " ").title()
    return None


def upload_video(endpoint, video_file, caption, title=None):
    """Upload a video to a given Graph API endpoint with optional thumbnail"""
    url = f"https://graph.facebook.com/v21.0/{PAGE_ID}/{endpoint}"
    params = {
        "access_token": ACCESS_TOKEN,
        "description": caption,
    }

    # Only include title if extracted
    if title:
        params["title"] = title

    files = {
        "source": open(video_file, "rb")
    }

    # Attach preview image if available
    if os.path.exists(PREVIEW_IMAGE):
        files["thumb"] = open(PREVIEW_IMAGE, "rb")

    response = requests.post(url, params=params, files=files)

    if response.status_code == 200:
        print(f"✅ Uploaded to {endpoint}:", response.json())
    else:
        print(f"❌ Error uploading to {endpoint}:", response.status_code, response.text)


def main():
    # Read caption
    with open(COMMENT_FILE, "r", encoding="utf-8") as f:
        caption = f.read().strip()

    # Read URL and extract title
    title = None
    if os.path.exists(URL_FILE):
        with open(URL_FILE, "r", encoding="utf-8") as f:
            url_text = f.read().strip()
            title = extract_title_from_url(url_text)
            print(f"📘 Extracted title: {title or 'None'}")

    # Upload full video with extracted title
    upload_video("videos", FULL_VIDEO, caption, title)


if __name__ == "__main__":
    main()