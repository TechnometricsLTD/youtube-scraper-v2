#!/usr/bin/env python3
"""
YouTube Search Script using yt-dlp
This script searches YouTube and returns search results with video information.
"""
import os
import hashlib
import datetime
from pathlib import Path
import subprocess
import sys
import yt_dlp
import json
from typing import List, Dict, Any, Optional


class YouTube:
    def __init__(self):
        """Initialize the YouTube searcher with yt-dlp configuration."""
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,  # Keep this True for speed
            'ignoreerrors': True,
        }
    
    def search_youtube(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search YouTube for videos matching the query.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            List[Dict]: List of video information dictionaries
        """

        print(f"🔍 Searching YouTube for: '{query}'")
        print(f"📊 Maximum results: {max_results}")
        try:
            # Use a faster search approach
            search_url = f"ytsearch{max_results}:{query}"
            
            # Optimized options for speed
            fast_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'ignoreerrors': True,
                'no_check_certificate': True,
                'extractor_retries': 1,
            }
            
            with yt_dlp.YoutubeDL(fast_opts) as ydl:
                # Extract video information
                results = ydl.extract_info(search_url, download=False)
                
                if not results or 'entries' not in results:
                    print(f"No results found for query: {query}")
                    return []
                
                videos = []
                for entry in results['entries']:
                    if entry:
                        video_info = {
                            'title': entry.get('title', 'Unknown'),
                            'url': entry.get('url', ''),
                            'webpage_url': entry.get('webpage_url', f"https://www.youtube.com/watch?v={entry.get('id', '')}"),
                            'duration': entry.get('duration', 0),
                            'view_count': entry.get('view_count', 0),
                            'uploader': entry.get('uploader', 'Unknown'),
                            'thumbnail': entry.get('thumbnail', ''),
                            'id': entry.get('id', ''),
                        }
                        videos.append(video_info)
                print("✅ Search completed successfully")
                return videos
                
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            return []
    
    def format_duration(self, seconds: int) -> str:
        """Convert seconds to human-readable duration format."""
        if not seconds:
            return "Unknown"
        
        # Convert to int in case it's a float
        seconds = int(seconds)
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
    
    def format_view_count(self, count: int) -> str:
        """Format view count with K, M, B suffixes."""
        if not count:
            return "Unknown"
        
        if count >= 1000000000:
            return f"{count / 1000000000:.1f}B"
        elif count >= 1000000:
            return f"{count / 1000000:.1f}M"
        elif count >= 1000:
            return f"{count / 1000:.1f}K"
        else:
            return str(count)
    
    def display_results(self, videos: List[Dict[str, Any]], query: str):
        """Display search results in a formatted way."""
        if not videos:
            print(f"No results found for: {query}")
            return
        
        print(f"\n📺 YouTube Search Results for: '{query}'")
        print("=" * 80)
        
        for i, video in enumerate(videos, 1):
            print(f"\n{i}. {video['title']}")
            print(f"   👤 Uploader: {video['uploader']}")
            print(f"   ⏱️  Duration: {self.format_duration(video['duration'])}")
            print(f"   👁️  Views: {self.format_view_count(video['view_count'])}")
            
            # Handle URL
            webpage_url = video['webpage_url']
            if webpage_url:
                print(f"   🔗 URL: {webpage_url}")
            else:
                print(f"   🔗 URL: https://www.youtube.com/watch?v={video['id']}")
            
            print("-" * 80)
    
    def save_results_to_json(self, videos: List[Dict[str, Any]], filename: str):
        """Save search results to a JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(videos, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Results saved to: {filename}")
        except Exception as e:
            print(f"Error saving results: {e}")
    def download_video_info(self, url):
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
            "_id": {
                "$oid": hashlib.md5(url.encode()).hexdigest()
            },
            "type": "page",
            "source": "YouTube",
            "post_url": url,
            "post_title": video_info.get("title", None),
            "posted_at": {
                "$date": current_time
            },
            "post_text": video_info.get("description", ""),
            "post_topic": {
                "status": "ok",
                "topic": {
                    "label": "video",
                    "score": 0.8
                }
            },
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
                    "id": comment_id,
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
                        child_copy.pop("parent", None)
                        child_copy.pop("id", None)
                        comment["comments_replies"].append(child_copy)
                
                # Add to formatted data, removing the processing fields
                comment_copy = comment.copy()
                comment_copy.pop("parent", None)
                comment_copy.pop("id", None)
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
        formatted_data["percent_comments"] = 0.5
        formatted_data["total_shares"] = 0  # Setting to 0 since YouTube doesn't provide share count
        formatted_data["vitality_score"] = video_info.get("view_count", 0) // 1000  # Using view_count for vitality
        formatted_data["checksum"] = hashlib.md5(json.dumps(formatted_data["comments"]).encode()).hexdigest()
        
        # Create directories if they don't exist
        Path("post_data/image").mkdir(parents=True, exist_ok=True)

        # Save formatted JSON
        '''output_file = f"post_data/{video_id}_formatted_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(formatted_data, f, indent=3, ensure_ascii=False)'''

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

        '''
        output_file = f"{video_id}" + "_formatted_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(formatted_data, f, indent=3, ensure_ascii=False)
        
        print(f"Comments and video info extracted and saved to {output_file}")
        print(f"Total comments from metadata: {comment_count}")
        print(f"Thumbnail saved")'''
        return formatted_data


def main():
    
    
    # Create searcher instance
    searcher = YouTube()
    
    # Perform search
    results = searcher.search_youtube("Younus", 20)
    searcher.display_results(results, "Younus")

    for result in results:
        print(result['url'])
        formatted_data = searcher.download_video_info(result['url'])
        print(formatted_data)
        print("--------------------------------")
    
    # Print summary
    print(f"\n✅ Found {len(results)} video(s) for query: 'Younus'")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Search interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
