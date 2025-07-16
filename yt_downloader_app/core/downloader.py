"""
Core download logic for YouTube videos and playlists.
"""
from pytube import YouTube, Playlist
import os

class DownloadError(Exception):
    pass

class Downloader:
    def __init__(self, save_path):
        self.save_path = save_path

    def download_video(self, url, quality=None, audio_only=False):
        try:
            yt = YouTube(url)
            if audio_only:
                stream = yt.streams.filter(only_audio=True).first()
            else:
                if quality:
                    stream = yt.streams.filter(res=quality, progressive=True).first()
                    if not stream:
                        stream = yt.streams.get_highest_resolution()
                else:
                    stream = yt.streams.get_highest_resolution()
            out_file = stream.download(output_path=self.save_path)
            return out_file
        except Exception as e:
            raise DownloadError(str(e))

    def download_playlist(self, playlist_url, quality=None, audio_only=False):
        try:
            pl = Playlist(playlist_url)
            files = []
            for url in pl.video_urls:
                file = self.download_video(url, quality, audio_only)
                files.append(file)
            return files
        except Exception as e:
            raise DownloadError(str(e))
