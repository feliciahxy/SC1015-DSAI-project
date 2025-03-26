import pandas as pd
import googleapiclient.discovery
import googleapiclient.errors
import isodate
import time
import os
import json
from datetime import datetime

def get_youtube_api_client(api_key):
    """
    Create a YouTube API client using an API key.
    
    Args:
        api_key (str): Your YouTube Data API key.
        
    Returns:
        googleapiclient.discovery.Resource: The YouTube API client
    """
    return googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

def get_video_details(youtube, video_ids, batch_size=50):
    """
    Get details for a list of YouTube videos including language and duration.
    
    Args:
        youtube: YouTube API client
        video_ids (list): List of YouTube video IDs
        batch_size (int): Number of videos to request at once (max 50)
        
    Returns:
        tuple: (dict of video details, bool indicating if quota was exceeded)
    """
    results = {}
    quota_exceeded = False
    
    # Process video IDs in batches to respect API limits
    for i in range(0, len(video_ids), batch_size):
        batch = video_ids[i:i+batch_size]
        
        try:
            request = youtube.videos().list(
                part="snippet,contentDetails",
                id=",".join(batch)
            )
            response = request.execute()
            
            # Extract data from each video
            for item in response.get("items", []):
                video_id = item["id"]
                
                # Get language (defaultAudioLanguage or defaultLanguage)
                snippet = item.get("snippet", {})
                language = snippet.get("defaultAudioLanguage", 
                           snippet.get("defaultLanguage", "unknown"))
                
                # Get duration
                content_details = item.get("contentDetails", {})
                duration_iso = content_details.get("duration", "PT0S")  # Default to 0 seconds
                duration_seconds = int(isodate.parse_duration(duration_iso).total_seconds())
                
                # Store results
                results[video_id] = {
                    "video_language": language,
                    "video_length": duration_seconds
                }
            
            print(f"Processed batch {i//batch_size + 1}/{(len(video_ids) + batch_size - 1)//batch_size} ({len(batch)} videos)")
            
            # Sleep to avoid hitting rate limits
            time.sleep(0.5)
            
        except googleapiclient.errors.HttpError as e:
            print(f"HTTP Error: {e}")
            
            # If quota exceeded, flag it and stop processing
            if "quotaExceeded" in str(e):
                print("Quota exceeded! Saving progress and exiting...")
                quota_exceeded = True
                break
            
            # For other errors, wait and continue
            print("Waiting 10 seconds before continuing...")
            time.sleep(10)
            continue
            
    return results, quota_exceeded

def save_progress(processed_ids, save_file="youtube_api_progress.json"):
    """
    Save the IDs of videos already processed to a file.
    
    Args:
        processed_ids (list): List of video IDs that have been processed
        save_file (str): Path to save the progress file
    """
    data = {
        "last_updated": datetime.now().isoformat(),
        "processed_ids": processed_ids
    }
    
    with open(save_file, "w") as f:
        json.dump(data, f)
    
    print(f"Progress saved: {len(processed_ids)} videos processed so far")

def load_progress(save_file="youtube_api_progress.json"):
    """
    Load the IDs of videos that were already processed.
    
    Args:
        save_file (str): Path to the progress file
        
    Returns:
        list: List of video IDs that have been processed
    """
    if not os.path.exists(save_file):
        return []
    
    with open(save_file, "r") as f:
        data = json.load(f)
    
    processed_ids = data.get("processed_ids", [])
    last_updated = data.get("last_updated", "unknown")
    
    print(f"Loaded progress from {last_updated}: {len(processed_ids)} videos already processed")
    return processed_ids

def enrich_youtube_data(input_file, output_file, api_key, progress_file="youtube_api_progress.json"):
    """
    Add video language and length data to a CSV file of YouTube trending videos.
    Supports incremental processing by saving and loading progress.
    
    Args:
        input_file (str): Path to the input CSV file
        output_file (str): Path to save the enriched CSV file
        api_key (str): Your YouTube Data API key
        progress_file (str): Path to save/load progress
    """
    print(f"Reading data from {input_file}...")
    
    # Read the processed CSV file
    df = pd.read_csv(input_file)
    
    # Check if output file already exists (for incremental updates)
    if os.path.exists(output_file):
        print(f"Output file {output_file} already exists. Loading for incremental update...")
        output_df = pd.read_csv(output_file)
        
        # Use the output file if it has the required columns and matches the input file structure
        if 'video_language' in output_df.columns and 'video_length' in output_df.columns:
            df = output_df
            print(f"Loaded existing enriched data with {len(df)} videos")
    else:
        # Initialize new columns with default values if they don't exist
        if 'video_language' not in df.columns:
            df['video_language'] = 'unknown'
        if 'video_length' not in df.columns:
            df['video_length'] = 0
    
    # Load previously processed video IDs
    processed_ids = load_progress(progress_file)
    
    # Extract all video IDs from the dataset that haven't been processed yet
    all_video_ids = df['video_id'].tolist()
    # Clean video IDs (remove quotes if present)
    all_video_ids = [vid.strip('"') for vid in all_video_ids]
    
    # Filter out already processed IDs
    video_ids_to_process = [vid for vid in all_video_ids if vid not in processed_ids]
    
    print(f"Total videos: {len(all_video_ids)}")
    print(f"Already processed: {len(processed_ids)}")
    print(f"Remaining to process: {len(video_ids_to_process)}")
    
    if not video_ids_to_process:
        print("All videos have been processed! No API calls needed.")
        return df
    
    # Initialize the YouTube API client
    youtube = get_youtube_api_client(api_key)
    
    # Get video details from the YouTube API
    print("Fetching video details from YouTube API...")
    video_details, quota_exceeded = get_video_details(youtube, video_ids_to_process)
    
    # Update values for videos that we found details for
    videos_updated = 0
    for i, row in df.iterrows():
        video_id = row['video_id'].strip('"')
        if video_id in video_details:
            df.at[i, 'video_language'] = video_details[video_id]['video_language']
            df.at[i, 'video_length'] = video_details[video_id]['video_length']
            videos_updated += 1
            
            # Add this ID to the processed list
            if video_id not in processed_ids:
                processed_ids.append(video_id)
    
    # Save the enriched data
    df.to_csv(output_file, index=False)
    print(f"Enriched data saved to {output_file}")
    
    # Save progress for next run
    save_progress(processed_ids, progress_file)
    
    # Print some stats
    print(f"Updated {videos_updated} videos in this session")
    print(f"Total videos processed so far: {len(processed_ids)}/{len(all_video_ids)} ({len(processed_ids)/len(all_video_ids)*100:.1f}%)")
    
    if quota_exceeded:
        print("API quota was exceeded. Run the script again later to continue processing.")
    elif len(processed_ids) < len(all_video_ids):
        print("There are still videos to process. Run the script again to continue.")
    else:
        print("All videos have been processed successfully!")
    
    return df

if __name__ == "__main__":
    input_file = "/Users/selen/repos/SC1015-DSAI-project/datasets/cleaned/cleaned_youtube_trending.csv"
    output_file = "/Users/selen/repos/SC1015-DSAI-project/datasets/final/complete_youtube_trending.csv"
    progress_file = "youtube_api_progress.json"
    
    # Replace with your actual YouTube Data API key
    # You can get one from https://console.developers.google.com/
    api_key = "AIzaSyDtRdOzAYhaEeROHrHSvX6By6Tv0vN_afM"
    
    enriched_data = enrich_youtube_data(input_file, output_file, api_key, progress_file)