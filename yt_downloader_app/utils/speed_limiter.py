"""
Download speed limiter utility for YouTube Video Downloader.
"""
import time

def limit_speed(chunk_size, speed_limit):
    """
    chunk_size: bytes per chunk
    speed_limit: bytes per second
    """
    sleep_time = chunk_size / speed_limit
    time.sleep(sleep_time)
