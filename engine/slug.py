# file: reuters_news_module.py  

import requests  
import json  
import base64  
import re  
from datetime import datetime  
import os  
import random  
  
HOME_DIR = os.path.join(os.path.dirname(__file__), "..")  # reference to home folder  
  
def fetch_reuters_json():  
    """Fetch latest Reuters news JSON and save to home folder."""  
    url = "https://www.reutersconnect.com/featured-collection/latest-news/video?categories=news&sort=newest-first"  
  
    headers = {  
        "Cookie": "OptanonConsent=isGpcEnabled=0&datestamp=Wed+Sep+17+2025+18%3A40%3A40+GMT%2B0000+(Coordinated+Universal+Time)&version=202505.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=1%3A1%2C3%3A1%2CSPD_BG%3A1%2C2%3A1%2C4%3A1&AwaitingReconsent=false&geolocation=NG%3BRI; datadome=QJ_fjKk3NM1Z5AE5XOKjXBHEsMcGGObeABec4tGInCx3gkJvxF7YJG2DprDZuNn3LCvOiqDAVwN5thGslj5uKJtLbZulRFcoa9qVPJkMMBRUi~AFaJ~orCUj4fUaf5RT; ajs_anonymous_id=a9a1ef17-e21e-4037-ba9a-ae84b9a6826d; OptanonAlertBoxClosed=2025-09-17T18:40:39.671Z",  
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",  
        "Accept": "text/x-component",  
        "Accept-Language": "en-US,en;q=0.5",  
        "Accept-Encoding": "gzip, deflate, br",  
        "Referer": "https://www.reutersconnect.com/featured-collection/latest-news/video?categories=news&sort=newest-first",  
        "Next-Action": "3303cd16713262aa856a05c91ba627d4c3f3f3d4",  
        "Next-Router-State-Tree": "%5B%22%22%2C%7B%22children%22%3A%5B%22(public)%22%2C%7B%22children%22%3A%5B%22featured-collection%22%2C%7B%22children%22%3A%5B%5B%22titleSlug%22%2C%22latest-news%22%2C%22d%22%5D%2C%7B%22children%22%3A%5B%5B%22mediaType%22%2C%22video%22%2C%22oc%22%5D%2C%7B%22children%22%3A%5B%22__PAGE__%3F%7B%5C%22categories%5C%22%3A%5C%22news%5C%22%2C%5C%22sort%5C%22%3A%5C%22newest-first%5C%22%7D%22%2C%7B%7D%2C%22%2Ffeatured-collection%2Flatest-news%2Fvideo%3Fcategories%3Dnews%26sort%3Dnewest-first%22%2C%22refresh%22%5D%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D%7D%2Cnull%2Cnull%5D%7D%2Cnull%2Cnull%5D%7D%2Cnull%2Cnull%2Ctrue%5D",  
        "Content-Type": "text/plain;charset=UTF-8",  
        "Origin": "https://www.reutersconnect.com",  
        "Sec-Fetch-Dest": "empty",  
        "Sec-Fetch-Mode": "cors",  
        "Sec-Fetch-Site": "same-origin",  
        "Priority": "u=4",  
        "Te": "trailers",  
        "Connection": "keep-alive"  
    }  
  
    payload = [  
        {  
            "limit": 60,  
            "filter": {  
                "date": "",  
                "mediaTypes": ["video"],  
                "categories": ["news"],  
                "regions": [],  
                "sources": [],  
                "topicCodes": []  
            },  
            "sort": {"direction": "DESC", "field": "DATE"},  
            "query": "",  
            "cursor": ""  
        }  
    ]  
  
    response = requests.post(url, headers=headers, data=json.dumps(payload))  
  
    json_path = os.path.join(HOME_DIR, "reuter.json")  
    with open(json_path, "w", encoding="utf-8") as f:  
        f.write(response.text)  
  
    print(f"Response status: {response.status_code}")  
    print(f"Raw response saved to {json_path}")  
  
    try:  
        content = response.text  
        start = content.find("{")  
        end = content.rfind("}") + 1  
        if start == -1 or end == 0:  
            raise ValueError("No valid JSON object found in response")  
        json_str = content[start:end]  
        data = json.loads(json_str)  
        with open(json_path, "w", encoding="utf-8") as f:  
            json.dump(data, f, ensure_ascii=False, indent=4)  
        print("JSON parsed and saved successfully.")  
    except Exception as e:  
        print(f"Failed to parse JSON: {e}")  
        with open(json_path, "w", encoding="utf-8") as f:  
            json.dump({"value": {"items": []}}, f, ensure_ascii=False, indent=4)  
  
    return json_path  
  
def filter_and_save_url():  
    """Filter headlines using filter.json and save new URL and headline, skipping any that already exist."""  
    filter_path = os.path.join(HOME_DIR, "filter.json")  
    headlines_file = os.path.join(HOME_DIR, "headlines.txt")  
    url_file = os.path.join(HOME_DIR, "URL.txt")  
    reuter_path = os.path.join(HOME_DIR, "reuter.json")  
  
    with open(filter_path, "r", encoding="utf-8") as f:  
        filter_words = [w.lower() for w in json.load(f)]  
  
    with open(reuter_path, "r", encoding="utf-8") as f:  
        content = f.read()  
  
    start = content.find("{")  
    end = content.rfind("}") + 1  
    json_str = content[start:end]  
    try:  
        data = json.loads(json_str)  
    except json.JSONDecodeError:  
        data = {"value": {"items": []}}  
    items = data.get("value", {}).get("items", [])  
  
    def headline_matches(headline, keywords):  
        words = re.findall(r"[a-zA-Z]+", headline.lower())  
        return any(word in words for word in keywords)  
  
    def normalize_headline(headline):  
        if not headline:  
            return ""  
        headline = re.sub(r"\s+", " ", headline.strip())  
        headline = re.sub(r"[^\w\s-]", "", headline)  
        headline = headline.encode("ascii", "ignore").decode("ascii")  
        return headline.lower().strip()  
  
    today = datetime.now().strftime("%Y-%m-%d")  
  
    existing_headlines = set()  
    if os.path.exists(headlines_file):  
        with open(headlines_file, "r", encoding="utf-8") as f:  
            for line in f:  
                if " - " in line:  
                    try:  
                        headline = line.strip().split(" - ", 1)[1]  
                        normalized = normalize_headline(headline)  
                        if normalized:  
                            existing_headlines.add(normalized)  
                    except IndexError:  
                        continue  
  
    saved_url = None  
    saved_headline = None  
    match_count = 0  
    max_attempts = 3  
    non_existing_candidates = []  
  
    for item in items:  
        headline = item.get("headline", "")  
        uri = item.get("uri", "")  
        if not headline or not uri:  
            continue  
  
        normalized_headline = normalize_headline(headline)  
        if normalized_headline in existing_headlines:  
            continue  # skip if already exists  
  
        slug = re.sub(r"[^a-zA-Z0-9\s-]", "", headline)  
        slug = re.sub(r"\s+", "-", slug.strip()).lower()  
        uri_b64 = base64.b64encode(uri.encode("utf-8")).decode("utf-8")  
        candidate_url = f"https://www.reutersconnect.com/item/{slug}/{uri_b64}"  
  
        non_existing_candidates.append((headline, candidate_url))  
  
        if headline_matches(headline, filter_words):  
            match_count += 1  
            if match_count <= max_attempts:  
                saved_headline = headline  
                saved_url = candidate_url  
                break  
  
    # If no keyword match, select a random non-existing headline that isn't already saved  
    if not saved_url and non_existing_candidates:  
        available = [h for h in non_existing_candidates if normalize_headline(h[0]) not in existing_headlines]  
        if available:  
            saved_headline, saved_url = random.choice(available)  
  
    if saved_url and saved_headline:  
        with open(url_file, "w", encoding="utf-8") as f:  
            f.write(saved_url + "\n")  
  
        with open(headlines_file, "a", encoding="utf-8") as f:  
            f.write(f"{today} - {saved_headline}\n")  
  
        print(f"One! Saved headline and URL{' after ' + str(match_count) + ' attempt(s)' if match_count else ''}.")  
        return saved_headline, saved_url  
    else:  
        print("No new headlines found.")  
        return None, None  
  
def run():  
    fetch_reuters_json()  
    return filter_and_save_url()
