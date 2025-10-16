# main.py
# Location: news/main.py
# Engine folder: news/engine/

import os
import sys
import time
import subprocess

# Add engine folder to Python path
ENGINE_PATH = os.path.join(os.path.dirname(__file__), "engine")
if ENGINE_PATH not in sys.path:
    sys.path.insert(0, ENGINE_PATH)

# Import the run functions from your existing files
from slug import run as run_news
from stream import run as run_stream
from downloader import run as run_download

# Helper to run shell commands or Python scripts
def run_command(command, cwd=None):
    """Run a shell command or Python script; returns True on success"""
    try:
        result = subprocess.run(command, shell=True, check=True, cwd=cwd,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}")
        print(e.stderr)
        return False

def run_pipeline():
    while True:
        # Step 1: Fetch news
        print("Fetching latest news...")
        news_result = run_news()
        if not news_result:
            print("Failed to fetch news. Retrying...")
            time.sleep(2)
            continue

        # Step 2: Fetch video stream
        print("Fetching video stream URL...")
        stream_result = run_stream()
        if not stream_result:
            print("No video URL found ? refetching news...")
            time.sleep(1)
            continue  # rerun news

        # Step 3: Download video
        print("Downloading video...")
        download_result = run_download()
        if not download_result:
            print("Download failed ? refetching video stream URL...")
            time.sleep(1)
            continue  # rerun stream

        # Step 4: Run filter.sh
        print("Running filter.sh...")
        if not run_command("./filter.sh", cwd=os.path.dirname(__file__)):
            print("filter.sh failed, continuing...")

        # Step 5: Run gemini.py
        print("Running gemini.py...")
        if not run_command("python3 gemini.py", cwd=os.path.dirname(__file__)):
            print("gemini.py failed, continuing...")

        # Step 6: Run voice.py
        print("Running voice.py...")
        if not run_command("python3 voice.py", cwd=os.path.dirname(__file__)):
            print("voice.py failed, continuing...")

        # Step 7: Run vidmaker.sh
        print("Running vidmaker.sh...")
        if not run_command("./vidmaker.sh", cwd=os.path.dirname(__file__)):
            print("vidmaker.sh failed, continuing...")
            
        # Step 8: Run social.sh
        print("Running social.sh...")
        if not run_command("./social.sh", cwd=os.path.dirname(__file__)):
            print("social.sh failed, continuing...")
            
         # Step 9: Run comment.py
        print("Running comment.py...")
        if not run_command("python3 comment.py", cwd=os.path.dirname(__file__)):
            print("comment.py failed, continuing...")
            
         # Step 10: Run fb_post.py
        print("Running fb_post.py...")
        if not run_command("python3 fb_post.py", cwd=os.path.dirname(__file__)):
            print("fb_post.py failed, continuing...")
            
        # Step 10: Run yt_post.py
        print("Running yt_post.py...")
        if not run_command("python3 yt_post.py", cwd=os.path.dirname(__file__)):
            print("yt_post.py failed, continuing...")

        print("Pipeline complete!")
        break

if __name__ == "__main__":
    run_pipeline()
