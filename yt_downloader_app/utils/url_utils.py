"""
URL sanitization and validation for YouTube Video Downloader.
"""
import re
from urllib.parse import urlparse, parse_qs

def sanitize_youtube_url(url):
    """
    Returns a clean YouTube video or playlist URL (removes extra params, handles youtu.be).
    """
    if 'youtu.be/' in url:
        # Convert youtu.be short link to full link
        video_id = url.split('youtu.be/')[-1].split('?')[0]
        return f'https://www.youtube.com/watch?v={video_id}'
    if 'watch?v=' in url:
        # Remove extra params, keep only v and list if present
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        base = 'https://www.youtube.com/watch?v=' + qs.get('v', [''])[0]
        if 'list' in qs:
            base += f'&list={qs["list"][0]}'
        return base
    if 'playlist?list=' in url:
        # Remove extra params, keep only list
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        return f'https://www.youtube.com/playlist?list={qs.get("list", [""])[0]}'
    return url

def is_youtube_url(url):
    return 'youtube.com' in url or 'youtu.be' in url
