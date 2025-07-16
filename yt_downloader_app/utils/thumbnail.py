"""
Video thumbnail fetcher for YouTube Video Downloader.
"""
from pytube import YouTube
import requests
from PIL import Image, ImageTk
from io import BytesIO

def fetch_thumbnail(url):
    yt = YouTube(url)
    thumb_url = yt.thumbnail_url
    response = requests.get(thumb_url)
    img = Image.open(BytesIO(response.content))
    return img

# For Tkinter display

def get_tk_thumbnail(url, size=(160, 90)):
    img = fetch_thumbnail(url)
    img = img.resize(size, Image.ANTIALIAS)
    return ImageTk.PhotoImage(img)
