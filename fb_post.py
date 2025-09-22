import requests

PAGE_ID = "796052743592190"
ACCESS_TOKEN = "EAAVQdbJuFuMBPq50S5TCV29w998qEKaBiqzsHuQrKqwxe8vAgSdsbq3d2Q77WiIgasBJZAkWq4ljHOnLap7r0LAcZBrQp1fPrLxNMRIe8uOfrbBgt5RmHat08wYBazH5uiTu4VBwbJzDbDZA19UaiYLHkT3nusQXaE4FNXZCDCkVkC7W3KOd8LChHgpkq8IkA1KZAsZA7B"

VIDEO_FILE = "news.mp4"
COMMENT_FILE = "comment.txt"


def post_video_to_facebook(video_file, comment_file):
    # Read caption from comment.txt
    with open(comment_file, "r", encoding="utf-8") as f:
        caption = f.read().strip()

    url = f"https://graph.facebook.com/v21.0/{PAGE_ID}/videos"
    params = {
        "access_token": ACCESS_TOKEN,
        "description": caption,
        "title": "Automated Upload"
    }

    files = {
        "source": open(video_file, "rb")
    }

    response = requests.post(url, params=params, files=files)

    if response.status_code == 200:
        print("✅ Video uploaded successfully:", response.json())
    else:
        print("❌ Error:", response.status_code, response.text)


if __name__ == "__main__":
    post_video_to_facebook(VIDEO_FILE, COMMENT_FILE)