"""
Main application window for YouTube Video Downloader.
"""

import ttkbootstrap as tb
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .widgets import LabeledEntry
from ..core.manager import DownloadManager
from ..utils.history import HistoryManager
from ..utils.clipboard import get_clipboard_text
from ..utils.url_utils import sanitize_youtube_url, is_youtube_url
import threading


class MainWindow(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill=tk.BOTH, expand=True)
        self.save_path = tk.StringVar(value="downloads")
        self.quality = tk.StringVar(value="720p")
        self.audio_only = tk.BooleanVar(value=False)
        self.urls = []
        self.history = HistoryManager()
        self.manager = DownloadManager(self.save_path.get())
        self.create_widgets()

    def create_widgets(self):
        # URL input
        url_frame = ttk.LabelFrame(self, text="Video/Playlist URLs")
        url_frame.pack(fill=tk.X, padx=20, pady=10)
        self.url_entry = LabeledEntry(url_frame, "URL:", width=60)
        self.url_entry.pack(side=tk.LEFT, padx=5, pady=5)
        paste_btn = ttk.Button(url_frame, text="Paste", command=self.paste_url)
        paste_btn.pack(side=tk.LEFT, padx=5)
        add_btn = ttk.Button(url_frame, text="Add", command=self.add_url)
        add_btn.pack(side=tk.LEFT, padx=5)
        clear_btn = ttk.Button(url_frame, text="Clear", command=self.clear_urls)
        clear_btn.pack(side=tk.LEFT, padx=5)

        # URL list
        self.url_listbox = tk.Listbox(self, height=5)
        self.url_listbox.pack(fill=tk.X, padx=20)

        # Quality selection
        options_frame = ttk.LabelFrame(self, text="Options")
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(options_frame, text="Quality:").pack(side=tk.LEFT, padx=5)
        quality_combo = ttk.Combobox(options_frame, textvariable=self.quality, values=["144p","240p","360p","480p","720p","1080p"], width=8)
        quality_combo.pack(side=tk.LEFT, padx=5)
        audio_chk = ttk.Checkbutton(options_frame, text="Audio Only (MP3)", variable=self.audio_only)
        audio_chk.pack(side=tk.LEFT, padx=5)
        ttk.Label(options_frame, text="Save to:").pack(side=tk.LEFT, padx=5)
        save_entry = ttk.Entry(options_frame, textvariable=self.save_path, width=20)
        save_entry.pack(side=tk.LEFT, padx=5)
        browse_btn = ttk.Button(options_frame, text="Browse", command=self.browse_folder)
        browse_btn.pack(side=tk.LEFT, padx=5)

        # Download controls
        ctrl_frame = ttk.Frame(self)
        ctrl_frame.pack(fill=tk.X, padx=20, pady=10)
        download_btn = ttk.Button(ctrl_frame, text="Download", command=self.start_download)
        download_btn.pack(side=tk.LEFT, padx=5)
        pause_btn = ttk.Button(ctrl_frame, text="Pause", command=self.pause_download)
        pause_btn.pack(side=tk.LEFT, padx=5)
        resume_btn = ttk.Button(ctrl_frame, text="Resume", command=self.resume_download)
        resume_btn.pack(side=tk.LEFT, padx=5)

        # Progress bar
        self.progress = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=600, mode='determinate')
        self.progress.pack(padx=20, pady=10)

        # Status
        self.status = ttk.Label(self, text="Ready", font=("Arial", 12))
        self.status.pack(padx=20, pady=5)

        # History
        history_frame = ttk.LabelFrame(self, text="Download History")
        history_frame.pack(fill=tk.BOTH, padx=20, pady=10, expand=True)
        self.history_listbox = tk.Listbox(history_frame, height=6)
        self.history_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.update_history()

    def paste_url(self):
        text = get_clipboard_text()
        self.url_entry.set(text)

    def add_url(self):
        url = self.url_entry.get().strip()
        if url and is_youtube_url(url):
            clean_url = sanitize_youtube_url(url)
            self.urls.append(clean_url)
            self.url_listbox.insert(tk.END, clean_url)
            self.url_entry.set("")

    def clear_urls(self):
        self.urls.clear()
        self.url_listbox.delete(0, tk.END)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.save_path.set(folder)
            self.manager.downloader.save_path = folder

    def start_download(self):
        if not self.urls:
            messagebox.showwarning("No URLs", "Please add at least one video or playlist URL.")
            return
        # Sanitize all URLs before download
        self.urls = [sanitize_youtube_url(url) for url in self.urls if is_youtube_url(url)]
        self.status.config(text="Downloading...")
        self.progress['value'] = 0
        self.progress['maximum'] = 100
        self.completed_files = 0
        self.total_files = len(self.urls)

        def progress_callback(d):
            if d.get('status') == 'downloading':
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes', 0)
                percent = 0
                if total_bytes:
                    percent = downloaded / total_bytes * 100
                # Schedule update in main thread
                self.progress.after(0, lambda: self.progress.configure(value=percent))
                self.status.after(0, lambda: self.status.config(text=f"Downloading: {d.get('filename', '')} ({percent:.1f}%) | Completed: {self.completed_files}/{self.total_files}"))
            elif d.get('status') == 'finished':
                self.progress.after(0, lambda: self.progress.configure(value=100))
                self.status.after(0, lambda: self.status.config(text=f"Downloaded: {d.get('filename', '')} | Completed: {self.completed_files+1}/{self.total_files}"))

        def callback(url, file, error):
            if error:
                self.status.config(text=f"Error: {error}")
            else:
                self.completed_files += 1
                self.status.config(text=f"Downloaded: {file} | Completed: {self.completed_files}/{self.total_files}")
                self.history.add({"url": url, "file": file})
                self.update_history()
            self.progress['value'] = 0

        threading.Thread(target=self.manager.bulk_download, args=(self.urls, self.quality.get(), self.audio_only.get(), callback, progress_callback)).start()

    def pause_download(self):
        self.manager.pause()
        self.status.config(text="Paused (current file will finish, queue is paused)")

    def resume_download(self):
        self.manager.resume()
        self.status.config(text="Resumed")

    def update_history(self):
        self.history_listbox.delete(0, tk.END)
        for entry in self.history.get_all():
            self.history_listbox.insert(tk.END, f"{entry['url']} -> {entry['file']}")
