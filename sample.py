'''this code demostrates how to retreive the video length (from a list of video ids) from Youtube API'''

import os
import googleapiclient.discovery
import re
import pandas as pd

# Set up API credentials
api_key = "YOUR_API_KEY"
youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

# Your list of video IDs
video_ids = [
    "dQw4w9WgXcQ",  # Example video ID
    "jNQXAC9IVRw",  # Example video ID
    # Add more video IDs here
]

# Function to parse ISO 8601 duration to seconds
def parse_duration(duration):
    match = re.match(r'PT(\d+H)?(\d+M)?(\d+S)?', duration)
    if not match:
        return 0
    
    hours = match.group(1)[:-1] if match.group(1) else 0
    minutes = match.group(2)[:-1] if match.group(2) else 0
    seconds = match.group(3)[:-1] if match.group(3) else 0
    
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds)

# Collect data in batches (max 50 IDs per request)
all_videos = []
batch_size = 50

for i in range(0, len(video_ids), batch_size):
    batch = video_ids[i:i+batch_size]
    
    request = youtube.videos().list(
        part="snippet,contentDetails",
        id=",".join(batch)
    )
    
    response = request.execute()
    
    for video in response["items"]:
        video_data = {
            "id": video["id"],
            "title": video["snippet"]["title"],
            "channel": video["snippet"]["channelTitle"],
            "duration_raw": video["contentDetails"]["duration"],
            "duration_seconds": parse_duration(video["contentDetails"]["duration"]),
            "published_at": video["snippet"]["publishedAt"]
        }
        all_videos.append(video_data)

# Create DataFrame
df = pd.DataFrame(all_videos)

# Save to CSV
df.to_csv("youtube_video_durations.csv", index=False)