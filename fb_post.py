import subprocess
import requests
import os

PAGE_ID = "796052743592190"
ACCESS_TOKEN = "EAAVQdbJuFuMBPq50S5TCV29w998qEKaBiqzsHuQrKqwxe8vAgSdsbq3d2Q77WiIgasBJZAkWq4ljHOnLap7r0LAcZBrQp1fPrLxNMRIe8uOfrbBgt5RmHat08wYBazH5uiTu4VBwbJzDbDZA19UaiYLHkT3nusQXaE4FNXZCDCkVkC7W3KOd8LChHgpkq8IkA1KZAsZA7B"

FULL_VIDEO = "news.mp4"
REEL_VIDEO = "news_reel.mp4"
COMMENT_FILE = "comment.txt"
PREVIEW_IMAGE = "preview.jpg"


def trim_video(input_file, output_file, duration=90):
    """Trim the first `duration` seconds of the video"""
    if os.path.exists(output_file):
        os.remove(output_file)

    cmd = [
        "ffmpeg",
        "-y",  # overwrite output file
        "-i", input_file,
        "-t", str(duration),
        "-c", "copy",
        output_file
    ]
    subprocess.run(cmd, check=True)
    print(f"🎬 Trimmed reel saved to {output_file}")


def upload_video(endpoint, video_file, caption):
    """Upload a video to a given Graph API endpoint with optional thumbnail"""
    url = f"https://graph.facebook.com/v21.0/{PAGE_ID}/{endpoint}"
    params = {
        "access_token": ACCESS_TOKEN,
        "description": caption,
        "title": "Automated Upload"
    }
    files = {
        "source": open(video_file, "rb")
    }

    # Attach preview.jpg if available
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

    # Step 1: Trim first 90s for Reels
    trim_video(FULL_VIDEO, REEL_VIDEO, duration=90)

    # Step 2: Upload Reel with preview.jpg as thumbnail
    upload_video("video_reels", REEL_VIDEO, caption + "\n\n▶ Full video on our Page!")

    # Step 3: Upload Full Video with preview.jpg as thumbnail
    upload_video("videos", FULL_VIDEO, caption)


if __name__ == "__main__":
    main()