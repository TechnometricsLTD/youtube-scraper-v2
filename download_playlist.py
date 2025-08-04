import yt_dlp
import json
import sys
import requests
import re
from dataclasses import dataclass


@dataclass
class YoutubeVideo:
    id: str
    title: str
    source: str
    description: str
    url: str
    upload_date: str = None
    metadata: dict = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'source': self.source,
            'description': self.description,
            'url': self.url,
            'upload_date': self.upload_date,
            'metadata': self.metadata
        }

@dataclass
class YoutubePlaylist:
    id: str
    title: str
    description: str
    url: str
    channel_id: str
    videos: list[YoutubeVideo]
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'channel_id': self.channel_id,
            'videos': [video.to_dict() for video in self.videos]
        }


def get_channel_id(channel_url):
    # Just extract the channel_id from the channel URL using yt-dlp's metadata extraction,
    # no need to fetch any playlist items or videos.
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'verbose': True,
        'progress': True,
        'yes_playlist': True,
        'playlist_items': '1',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        return info.get('channel_id')



def get_all_channel_video_details(uploads_playlist_url, limit=None):

    channel_id = get_channel_id(uploads_playlist_url)
    print(channel_id)

    uploads_playlist_id = f"https://www.youtube.com/playlist?list={'UU' + channel_id[2:]}"
    print(uploads_playlist_id)

    ydl_opts = {
        'quiet': False,
        'verbose': True,
        'extract_flat': 'in_playlist',  # Changed from True to 'in_playlist' to get more metadata
        'skip_download': True,
        'yes_playlist': True,
        'playlist_items': limit,
        'approximate_date': True,  # Get approximate upload dates
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist_info = ydl.extract_info(uploads_playlist_id, download=False)
    return formatted_playlist_info(playlist_info)
 
def get_all_playlist_video_details(playlist_url, limit=None):
    ydl_opts = {
        'quiet': False,
        'verbose': True,
        'extract_flat': 'in_playlist',  # Changed from True to 'in_playlist' to get more metadata
        'skip_download': True,
        'yes_playlist': True,
        'playlist_items': limit,
        'approximate_date': True,  # Get approximate upload dates
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist_info = ydl.extract_info(playlist_url, download=False)
    return formatted_playlist_info(playlist_info)

def formatted_playlist_info(playlist_info):
    videos = []
    for video in playlist_info.get("entries", []):
        videos.append(YoutubeVideo(
            id=video.get("id"),
            title=video.get("title"),
            description=video.get("description"),
            url=video.get("url"),
            source=video.get("channel"),
            upload_date=video.get("upload_date"),
            metadata=video
        ))
    
    youtube_playlist = YoutubePlaylist(
        id=playlist_info.get("id"),
        title=playlist_info.get("title"),
        description=playlist_info.get("description"),
        url=playlist_info.get("channel_url"),
        channel_id=playlist_info.get("channel_id"),
        videos=videos,
    )
    return youtube_playlist
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_playlist.py <channel_url>")
        sys.exit(1)
    channel_url = sys.argv[1]
    if len(sys.argv) > 2:
        limit = int(sys.argv[2])
    else:
        limit = None
    playlist_info = get_all_playlist_video_details(channel_url, limit)
    # Save to JSON file
    output_file = "uploads_playlist_videos.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(playlist_info.to_dict(), f, indent=2, ensure_ascii=False)
    # print(json.dumps(videos, indent=2, ensure_ascii=False))
    
