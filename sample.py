'''this code demostrates how to retreive the video length (from a list of video ids repeatedly) from Youtube API'''

import os
import time
import re
import pandas as pd
import googleapiclient.discovery
import googleapiclient.errors

def setup_youtube_api(api_key):
    """Initialize the YouTube API client."""
    return googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

def search_video_id(youtube, video_name):
    """Search for a video by name and return its ID."""
    try:
        request = youtube.search().list(
            part="id",
            maxResults=1,
            q=video_name,
            type="video"
        )
        response = request.execute()
        
        if response["items"]:
            return response["items"][0]["id"]["videoId"]
        return None
    except Exception as e:
        print(f"Error searching for video '{video_name}': {e}")
        return None

def parse_duration(duration):
    """Parse ISO 8601 duration format to seconds."""
    if not duration:
        return 0
        
    match = re.match(r'PT(\d+H)?(\d+M)?(\d+S)?', duration)
    if not match:
        return 0
    
    hours = int(match.group(1)[:-1]) if match.group(1) else 0
    minutes = int(match.group(2)[:-1]) if match.group(2) else 0
    seconds = int(match.group(3)[:-1]) if match.group(3) else 0
    
    return hours * 3600 + minutes * 60 + seconds

def format_duration(seconds):
    """Format seconds to HH:MM:SS."""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def get_video_details(youtube, video_ids):
    """Get video details for a list of video IDs."""
    video_data = []
    
    # Process in batches of 50 (API limit)
    for i in range(0, len(video_ids), 50):
        batch = [vid for vid in video_ids[i:i+50] if vid]  # Skip None values
        
        if not batch:
            continue
            
        try:
            request = youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=",".join(batch)
            )
            response = request.execute()
            
            for video in response.get("items", []):
                duration_raw = video["contentDetails"]["duration"]
                duration_seconds = parse_duration(duration_raw)
                
                data = {
                    "id": video["id"],
                    "title": video["snippet"]["title"],
                    "channel": video["snippet"]["channelTitle"],
                    "duration_raw": duration_raw,
                    "duration_seconds": duration_seconds,
                    "duration_formatted": format_duration(duration_seconds),
                    "view_count": video["statistics"].get("viewCount", "N/A"),
                    "like_count": video["statistics"].get("likeCount", "N/A"),
                    "published_at": video["snippet"]["publishedAt"]
                }
                video_data.append(data)
                
            # Respect API quotas
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error fetching details for batch {i//50 + 1}: {e}")
    
    return video_data

def process_video_names_csv(input_csv, name_column, api_key, output_csv=None):
    """
    Process a CSV file with video names, find their IDs, and get their details.
    
    Args:
        input_csv: Path to input CSV file
        name_column: Column name that contains video names
        api_key: YouTube Data API key
        output_csv: Path to output CSV file (default: input_filename_results.csv)
    
    Returns:
        DataFrame with video details
    """
    # Set default output filename if not provided
    if output_csv is None:
        base = os.path.splitext(input_csv)[0]
        output_csv = f"{base}_results.csv"
    
    # Initialize YouTube API
    youtube = setup_youtube_api(api_key)
    
    # Read input CSV
    try:
        df = pd.read_csv(input_csv)
        if name_column not in df.columns:
            raise ValueError(f"Column '{name_column}' not found in CSV. Available columns: {', '.join(df.columns)}")
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None
    
    video_names = df[name_column].tolist()
    total_videos = len(video_names)
    
    print(f"Processing {total_videos} video names...")
    
    # First, get video IDs for all names
    video_ids = []
    for i, name in enumerate(video_names):
        if i % 10 == 0:
            print(f"Searching IDs: {i}/{total_videos} ({i/total_videos*100:.1f}%)")
            
        video_id = search_video_id(youtube, name)
        video_ids.append(video_id)
        
        # Respect API quotas - search requests are more expensive (100 units each)
        time.sleep(1)
    
    # Get video details
    print("Retrieving video details...")
    video_data = get_video_details(youtube, video_ids)
    
    # Create DataFrame and include original video names
    result_df = pd.DataFrame(video_data)
    
    # Add the original search query to the results
    names_df = pd.DataFrame({
        'search_query': video_names,
        'video_id': video_ids
    })
    
    # Merge with the results
    if not result_df.empty:
        final_df = names_df.merge(result_df, left_on='video_id', right_on='id', how='left')
    else:
        final_df = names_df
    
    # Save to CSV
    final_df.to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")
    
    return final_df

if __name__ == "__main__":
    # Configuration
    API_KEY = "YOUR_API_KEY"  # Replace with your actual API key
    INPUT_CSV = "video_names.csv"  # Replace with your CSV file path
    VIDEO_NAME_COLUMN = "video_name"  # Replace with your column name
    
    # Process the CSV
    process_video_names_csv(INPUT_CSV, VIDEO_NAME_COLUMN, API_KEY)