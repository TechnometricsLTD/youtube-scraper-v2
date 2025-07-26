import subprocess
import sys
import json
import os
import datetime
import hashlib
from pathlib import Path

def download_video_info(url):
    info_json_filename = "post_data/video_info.json"
    comments_json_filename = "post_data/comments.json"
    
    # Download thumbnail and video info with comments
    print(f"Extracting video info and comments from: {url}")
    subprocess.run([
        sys.executable, "-m", "yt_dlp", url, 
        "--write-thumbnail", "--skip-download", "--write-info-json",
        "--write-comments", "--output", "%(id)s"
    ])
    
    # Find the info JSON file
    video_id = url.split('v=')[-1].split('&')[0] if 'v=' in url else url.split('/')[-1].split('?')[0]
    info_file = f"{video_id}.info.json"
    ss_file = f"{video_id}.webp"


    if not os.path.exists(info_file):
        print(f"Could not find info file: {info_file}")
        return
    
    # Load video info
    with open(info_file, 'r', encoding='utf-8') as f:
        video_info = json.load(f)
    
    # Save the original yt-dlp output before formatting
    # original_output_file = f"post_data/{video_id}_original_ytdlp.json"
    # with open(original_output_file, 'w', encoding='utf-8') as f:
    #     json.dump(video_info, f, indent=2, ensure_ascii=False)
    # print(f"Original yt-dlp output saved to: {original_output_file}")
    
    # Format datetime in standard format
    def format_date(timestamp):
        if isinstance(timestamp, int) or (isinstance(timestamp, str) and timestamp.isdigit()):
            # Convert unix timestamp to dd-MM-yyyy hh:mm format
            dt = datetime.datetime.fromtimestamp(int(timestamp))
            return dt.strftime("%d-%m-%Y %H:%M")
        elif isinstance(timestamp, str):
            # If it's already a string date but in wrong format
            try:
                dt = datetime.datetime.fromisoformat(timestamp)
                return dt.strftime("%d-%m-%Y %H:%M")
            except ValueError:
                pass
        # Default current time in proper format
        return datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    
    # Convert to specified format
    current_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    formatted_data = {
        "video_id": video_id,
        "type": "page",
        "source": "YouTube",
        "post_url": url,
        "post_title": video_info.get("title", None),
        "posted_at": {
            "$date": current_time
        },
        "post_text": video_info.get("description", ""),
        
        "comments": []
    }
    
    # First, create a dictionary to store all comments and replies by ID
    all_comments = {}
    
    # First pass: collect all comments and replies
    if "comments" in video_info:
        for item in video_info.get("comments", []):
            comment_id = item.get("id", "")
            timestamp = item.get("timestamp")
            formatted_timestamp = format_date(timestamp)
            
            comment_data = {
                "comment_id": comment_id,
                "parent": item.get("parent", ""),
                "user_pro_pic": item.get("author_thumbnail", ""),
                "comment_time": {
                    "$date": formatted_timestamp
                },
                "user_name": item.get("author", ""),
                "user_profile_url": item.get("author_url", ""),
                "comment_text": item.get("text", ""),
                "comments_replies": []
            }
            
            all_comments[comment_id] = comment_data
    
    # Create a mapping of parent IDs to lists of child comments
    parent_to_children = {}
    
    
    # Second pass: establish parent-child relationships
    for comment_id, comment in all_comments.items():
        parent = comment["parent"]
        
        # Skip root comments for now
        if parent != "root":
            # For replies, the ID format is parent_id.reply_id
            # Extract parent_id from the reply's parent field
            parent_id = parent
            
            if parent_id not in parent_to_children:
                parent_to_children[parent_id] = []
            
            parent_to_children[parent_id].append(comment)
    
    # Third pass: build the hierarchical structure
    for comment_id, comment in all_comments.items():
        # Only process root comments (these will be in the main comments array)
        if comment["parent"] == "root":
            # Add direct children
            if comment_id in parent_to_children:
                for child in parent_to_children[comment_id]:
                    # Remove the parent and id fields - they were just for processing
                    child_copy = child.copy()
                    # child_copy.pop("parent", None)
                    # child_copy.pop("id", None)
                    comment["comments_replies"].append(child_copy)
            
            # Add to formatted data, removing the processing fields
            comment_copy = comment.copy()
            # comment_copy.pop("parent", None)
            # comment_copy.pop("id", None)
            formatted_data["comments"].append(comment_copy)
    
    # Add reactions and other metadata
    formatted_data["reactions"] = {
        "Total": video_info.get("like_count", 0),
        "Sad": None,
        "Love": None,
        "Wow": None,
        "Like": video_info.get("like_count", 0),
        "Haha": None,
        "Angry": None
    }
    
    formatted_data["featured_image"] = [None] * 12
    
    # Use comment_count directly from video metadata if available
    comment_count = video_info.get("comment_count", 0)
    #if comment_count == 0:
        # If comment_count is not in metadata, count all comments including replies
    comment_count_scraped = len(video_info.get("comments", []))
    
    formatted_data["total_comments"] = comment_count
    formatted_data["total_comments_scraped"] = comment_count_scraped
    formatted_data["percent_comments"] = comment_count_scraped/comment_count
    formatted_data["total_shares"] = 0  # Setting to 0 since YouTube doesn't provide share count
    # formatted_data["vitality_score"] = video_info.get("view_count", 0) // 1000  # Using view_count for vitality
    formatted_data["checksum"] = hashlib.md5(
        (
            str(video_id) +
            str(formatted_data.get("posted_at", "")) +
            json.dumps(formatted_data["comments"], ensure_ascii=False)
        ).encode()
    ).hexdigest()
    
    # Create directories if they don't exist
    Path("post_data/image").mkdir(parents=True, exist_ok=True)

    # Save formatted JSON
    output_file = f"post_data/{video_id}_formatted_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(formatted_data, f, indent=4, ensure_ascii=False)

    # Rename the thumbnail file
    if os.path.exists(ss_file):
        new_ss_name = f"post_data/image/{video_id}_ss.webp"
        os.rename(ss_file, new_ss_name)
        print("File renamed successfully!")
    else:
        print("Original file not found.")

    # Move downloaded files to the correct directories
    if os.path.exists(f"{video_id}.info.json"):
        os.remove(f"{video_id}.info.json")

    if os.path.exists(f"{video_id}.webp"):
        os.remove(f"{video_id}.webp")

    
    output_file = f"{video_id}" + "_formatted_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(formatted_data, f, indent=3, ensure_ascii=False)
    
    print(f"Comments and video info extracted and saved to {output_file}")
    print(f"Total comments from metadata: {comment_count}")
    print(f"Thumbnail saved")

if __name__ == "__main__":
    url = "https://www.youtube.com/live/DD3JlT_u0DM?si=16IJzQz6vVebcMZM"
    download_video_info(url)