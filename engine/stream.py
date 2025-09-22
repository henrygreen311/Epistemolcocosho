# file: reuters_stream_module.py

import requests
import re
import time

def fetch_stream_json():
    """Fetch stream.json from ReutersConnect URL in URL.txt"""
    with open("URL.txt", "r", encoding="utf-8") as f:
        url = f.readline().strip()  # take the first URL only

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.reutersconnect.com/featured-collection/latest-news/video?categories=news&sort=newest-first",
        "Rsc": "1",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=4",
        "Te": "trailers",
        "Connection": "keep-alive"
    }

    response = requests.get(url, headers=headers)

    with open("stream.json", "w", encoding="utf-8") as f:
        f.write(response.text)

    print(f"Response status: {response.status_code}")
    print("Raw response saved to stream.json")
    return response.status_code

def extract_video_url():
    """Extract the first valid videoPreviewUrl from stream.json"""
    with open("stream.json", "r", encoding="utf-8") as f:
        content = f.read()

    matches = re.findall(r'"videoPreviewUrl"\s*:\s*"([^"]+)"', content)

    if not matches:
        print("No videoPreviewUrl found in stream.json — exiting.")
        return None

    for candidate in matches:
        if candidate and candidate[-1].isalpha():  # must end with alphabet
            return candidate
    return None

def fetch_and_save_video_url():
    """Fetch stream.json and extract a valid videoPreviewUrl once."""
    fetch_stream_json()
    saved_url = extract_video_url()
    
    if saved_url:
        with open("stream.txt", "w", encoding="utf-8") as f:
            f.write(saved_url + "\n")
        print("Done! First valid videoPreviewUrl saved to stream.txt")
        return saved_url
    else:
        print("Failed: No valid videoPreviewUrl found")
        return None  # explicit failure

def run():
    return fetch_and_save_video_url()