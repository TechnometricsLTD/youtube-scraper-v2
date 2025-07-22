import yt_dlp
import json
import sys

def get_channel_id(channel_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        return info.get('channel_id'), info


def get_video_details(video_url):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        return {
            "url": video_url,
            "title": info.get("title"),
            "description": info.get("description"),
            "like_count": info.get("like_count", 0)
        }


def get_all_channel_video_details(channel_url):
    channel_id, info = get_channel_id(channel_url)
    print(f"Channel ID: {channel_id}")
    # INSERT_YOUR_CODE
    if channel_id and len(channel_id) > 1:
        channel_id = channel_id[:1] + "U" + channel_id[2:]
    print(f"Channel ID: {channel_id}")
    # Go to the uploads playlist for the channel and get all video information
    uploads_playlist_url = f"https://www.youtube.com/playlist?list={channel_id}"
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'yes_playlist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist_info = ydl.extract_info(uploads_playlist_url, download=False)
        # Each entry in 'entries' is a video
        video_urls = []
        if 'entries' in playlist_info:
            for entry in playlist_info['entries']:
                if entry and 'url' in entry:
                    # entry['url'] is the video id, so construct full URL
                    video_urls.append(entry['url'])
    video_details = []
    print(f"Number of videos: {len(video_urls)}")
    for url in video_urls:
        try:
            details = get_video_details(url)
            video_details.append(details)
        except Exception as e:
            print(f"Failed to get info for {url}: {e}")
    return channel_id, video_details

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_playlist.py <channel_url>")
        sys.exit(1)
    channel_url = sys.argv[1]
    channel_id, videos = get_all_channel_video_details(channel_url)
    # Save to JSON file
    output_file = f"{channel_id}_videos.json" if channel_id else "channel_videos.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)
    print(json.dumps(videos['url'], indent=2, ensure_ascii=False))
    print(len(videos))
