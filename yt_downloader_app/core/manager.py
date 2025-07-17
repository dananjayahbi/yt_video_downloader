"""
Download manager for bulk, pause/resume, and error handling.
"""
from .downloader import Downloader, DownloadError
from .downloader_ytdlp import YtDlpDownloader, DownloadError as YtDlpError
import threading


class DownloadManager:
    def __init__(self, save_path):
        self.downloader = Downloader(save_path)
        self.ytdlp_downloader = YtDlpDownloader(save_path)
        self.active_threads = []
        self.paused = False

    def bulk_download(self, urls, quality=None, audio_only=False, callback=None, progress_callback=None):
        def worker(url):
            # Wait if paused (soft pause)
            while self.paused:
                import time; time.sleep(0.2)
            try:
                # Try yt-dlp first
                self.ytdlp_downloader.download(url, quality, audio_only, progress_callback=progress_callback)
                if callback:
                    callback(url, f"yt-dlp:{url}", None)
            except Exception as ytdlp_err:
                try:
                    # Fallback to pytube
                    file = self.downloader.download_video(url, quality, audio_only)
                    if callback:
                        callback(url, file, None)
                except Exception as e:
                    if callback:
                        callback(url, None, f"yt-dlp: {ytdlp_err}; pytube: {e}")
        self.active_threads = []
        for url in urls:
            t = threading.Thread(target=worker, args=(url,))
            t.start()
            self.active_threads.append(t)

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def is_active(self):
        return any(t.is_alive() for t in self.active_threads)
