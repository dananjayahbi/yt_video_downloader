"""
Alternative download logic using yt-dlp for YouTube videos and playlists.
"""
import yt_dlp
import os

class DownloadError(Exception):
    pass


class YtDlpDownloader:
    def __init__(self, save_path):
        self.save_path = save_path

    def download(self, url, quality=None, audio_only=False, progress_callback=None):
        def hook(d):
            if progress_callback:
                progress_callback(d)

        ydl_opts = {
            'outtmpl': os.path.join(self.save_path, '%(title)s.%(ext)s'),
            'noplaylist': False,
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [hook],
        }
        if audio_only:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        elif quality:
            ydl_opts['format'] = f'bestvideo[height<={quality.replace("p","")}]'+"+bestaudio/best"
        else:
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.download([url])
            return result
        except Exception as e:
            raise DownloadError(str(e))
