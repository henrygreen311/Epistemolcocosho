# file: reuters_download_module.py

import requests
import time

def read_video_url():
    """Read the first video URL from stream.txt"""
    try:
        with open("stream.txt", "r", encoding="utf-8") as f:
            video_url = f.readline().strip()
        if not video_url:
            print("No URL found in stream.txt")
            return None
        return video_url
    except FileNotFoundError:
        print("stream.txt not found")
        return None

def read_preview_url():
    """Read the first preview URL from preview.txt"""
    try:
        with open("preview.txt", "r", encoding="utf-8") as f:
            preview_url = f.readline().strip()
        if not preview_url:
            print("No URL found in preview.txt")
            return None
        return preview_url
    except FileNotFoundError:
        print("preview.txt not found")
        return None

def download_file(file_url, output_file):
    """Generic downloader for video/preview resources"""
    try:
        response = requests.get(file_url, stream=True)
    except Exception as e:
        print(f"Failed to download file: {e}")
        return False

    if response.status_code != 200:
        print(f"Failed to download file. HTTP status: {response.status_code}")
        return False

    total_downloaded = 0
    start_time = time.time()

    with open(output_file, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                total_downloaded += len(chunk)

                elapsed = time.time() - start_time
                if elapsed > 0:
                    rate_kb = (total_downloaded / 1024) / elapsed
                    print(f"\rDownloaded {total_downloaded/1024/1024:.2f} MB "
                          f"at {rate_kb:.2f} KB/s", end="")

    print(f"\nDownload complete: {output_file}")
    return True

def download_video(video_url, output_file="vid.MP4"):
    """Download video from URL and save to output_file"""
    return download_file(video_url, output_file)

def download_preview(preview_url, output_file="preview.jpg"):
    """Download preview from URL and save to output_file"""
    return download_file(preview_url, output_file)

def run():
    """Convenience function to read URLs and download them"""
    video_url = read_video_url()
    preview_url = read_preview_url()

    results = {"video": False, "preview": False}

    if video_url:
        results["video"] = download_video(video_url)
    else:
        print("Skipping video download.")

    if preview_url:
        results["preview"] = download_preview(preview_url)
    else:
        print("Skipping preview download.")

    return results