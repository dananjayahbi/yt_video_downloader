"""
File utility functions for YouTube Video Downloader.
"""
import os
import re

def safe_filename(name):
    # Remove invalid filename characters
    return re.sub(r'[\\/:*?"<>|]', '_', name)

def auto_rename(path):
    base, ext = os.path.splitext(path)
    i = 1
    new_path = path
    while os.path.exists(new_path):
        new_path = f"{base}({i}){ext}"
        i += 1
    return new_path
