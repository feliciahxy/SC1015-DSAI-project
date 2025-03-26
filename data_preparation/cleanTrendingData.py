import pandas as pd
import re
from datetime import datetime

def clean_youtube_data(input_file, output_file):
    """
    Process YouTube trending videos data by:
    1. Keeping only videos with trending dates from April 15, 2023 to April 15, 2024
    2. Changing description column to Y/N (has description or not)
    3. Changing tags column to count the number of tags
    
    Args:
        input_file (str): Path to the input CSV file
        output_file (str): Path to save the processed CSV file
    """
    print(f"Reading data from {input_file}...")
    
    # Read the CSV file - using a more tolerant approach
    # The data has quoted fields with commas inside them
    df = pd.read_csv(input_file, quotechar='"', escapechar='\\')
    
    print(f"Original data shape: {df.shape}")
    
    # Step 1: Modify description column to Y/N
    print("Modifying description column...")
    df['description'] = df['description'].apply(lambda x: 'Y' if pd.notna(x) and str(x).strip() != '' else 'N')
    
    # Step 2: Convert tags column to tag count
    print("Converting tags to tag count...")
    
    def count_tags(tags_str):
        if pd.isna(tags_str) or tags_str == '[None]' or not tags_str:
            return 0
        
        # Split by | which appears to be the tag delimiter in the sample data
        if '|' in str(tags_str):
            return len(str(tags_str).split('|'))
        
        # If no delimiter is found but there's content, assume it's one tag
        return 1 if str(tags_str).strip() else 0
    
    df['tags'] = df['tags'].apply(count_tags)
    
    # Step 3: Filter by trending date (April 15, 2023 to April 15, 2024)
    print("Filtering by trending date...")
    
    # First, convert trending_date to datetime
    try:
        df['trending_date'] = pd.to_datetime(df['trending_date'])
    except:
        # If that fails, try other common formats
        try:
            df['trending_date'] = pd.to_datetime(df['trending_date'], format='%Y-%m-%dT%H:%M:%SZ', errors='coerce')
        except:
            # If still failing, try with direct string format detection
            date_formats = ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%SZ', '%Y/%m/%d']
            
            for fmt in date_formats:
                try:
                    df['trending_date'] = pd.to_datetime(df['trending_date'], format=fmt, errors='coerce')
                    if not df['trending_date'].isna().all():
                        break
                except:
                    continue
    
    # Set date range for filtering - with timezone information
    # Make the start and end dates timezone-aware if the data is timezone-aware
    if hasattr(df['trending_date'].dt, 'tz') and df['trending_date'].dt.tz is not None:
        # If data has timezone info, add timezone to our filter dates
        start_date = pd.Timestamp('2023-04-15').tz_localize(df['trending_date'].dt.tz)
        end_date = pd.Timestamp('2024-04-15').tz_localize(df['trending_date'].dt.tz)
    else:
        # If data is timezone-naive, use naive timestamps
        start_date = pd.Timestamp('2023-04-15')
        end_date = pd.Timestamp('2024-04-15')
    
    # Filter the dataframe to include only rows within the date range
    filtered_df = df[(df['trending_date'] >= start_date) & 
                     (df['trending_date'] <= end_date)]
    
    print(f"Filtered data shape: {filtered_df.shape}")
    
    # Save the processed data
    filtered_df.to_csv(output_file, index=False, quoting=1)  # quoting=1 ensures fields with commas are properly quoted
    print(f"Processed data saved to {output_file}")
    
    return filtered_df


if __name__ == "__main__":
    input_file = "./datasets/original/US_youtube_trending_data_15_4_24.csv" 
    output_file = "./datasets/cleaned/cleaned_youtube_trending.csv"
    
    cleaned_data = clean_youtube_data(input_file, output_file)
    print("Data cleaning completed successfully.")