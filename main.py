#!/usr/bin/env python3
"""
YouTube Search Script using yt-dlp
This script searches YouTube and returns search results with video information.
"""

import yt_dlp
import json
import sys
from typing import List, Dict, Any, Optional
import argparse


class YouTubeSearcher:
    def __init__(self):
        """Initialize the YouTube searcher with yt-dlp configuration."""
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,  # Keep this True for speed
            'ignoreerrors': True,
        }
    
    def get_fast_upload_date(self, video_id: str) -> str:
        """Get upload date quickly for a single video."""
        try:
            opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'ignoreerrors': True,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
                return info.get('upload_date', '') if info else ''
        except:
            return ''
    
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


def main():
    
    
    # Create searcher instance
    searcher = YouTubeSearcher()
    
    # Perform search
    results = searcher.search_youtube("Younus", 20)
    searcher.display_results(results, "Younus")
    
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
