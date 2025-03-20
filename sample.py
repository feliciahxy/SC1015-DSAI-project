'''this code demostrates how to retreive the video length (for trending videos in US for a specific week in spr 2024) from Youtube API'''

import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import datetime
import time
import pandas as pd
import re

# Set up API credentials
api_key = "YOUR_API_KEY"
youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

# Define the date range (one week in April 2024)
start_date = datetime.date(2024, 4, 1)  # Adjust to your desired week
days = 7

# Function to parse ISO 8601 duration to seconds
def parse_duration(duration):
    match = re.match(r'PT(\d+H)?(\d+M)?(\d+S)?', duration)
    if not match:
        return 0
    
    hours = match.group(1)[:-1] if match.group(1) else 0
    minutes = match.group(2)[:-1] if match.group(2) else 0
    seconds = match.group(3)[:-1] if match.group(3) else 0
    
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds)

# Collect data for each day
all_videos = []

for day in range(days):
    current_date = start_date + datetime.timedelta(days=day)
    print(f"Collecting data for {current_date}")
    
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        chart="mostPopular",
        regionCode="US",
        maxResults=50
    )
    
    response = request.execute()
    
    for video in response["items"]:
        video_data = {
            "date": current_date.strftime("%Y-%m-%d"),
            "id": video["id"],
            "title": video["snippet"]["title"],
            "channel": video["snippet"]["channelTitle"],
            "duration_raw": video["contentDetails"]["duration"],
            "duration_seconds": parse_duration(video["contentDetails"]["duration"]),
            "views": video["statistics"]["viewCount"],
            "likes": video["statistics"].get("likeCount", 0),
            "comments": video["statistics"].get("commentCount", 0)
        }
        all_videos.append(video_data)
    
    # Respect API quota limits - wait before next request
    time.sleep(5)

# Create DataFrame
df = pd.DataFrame(all_videos)

# Save to CSV
df.to_csv("youtube_trending_april_2024.csv", index=False)