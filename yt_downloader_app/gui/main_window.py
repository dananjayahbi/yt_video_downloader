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
from PIL import Image, ImageTk
import os
import subprocess


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

        # Load spinner GIF
        self.spinner_frames = []
        try:
            spinner_gif = Image.open("assets/spinner.gif")
            for frame in range(spinner_gif.n_frames):
                spinner_gif.seek(frame)
                frame_image = ImageTk.PhotoImage(spinner_gif.copy())
                self.spinner_frames.append(frame_image)
        except Exception as e:
            print("Error loading spinner GIF:", e)

        self.spinner_label = ttk.Label(self)
        self.spinner_label.pack_forget()  # Initially hidden

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

        # Add scrollbars to URL list and History
        url_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.url_listbox.yview)
        self.url_listbox.configure(yscrollcommand=url_scrollbar.set)
        url_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

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
        open_folder_btn = ttk.Button(ctrl_frame, text="Open Folder", command=self.open_download_folder)
        open_folder_btn.pack(side=tk.LEFT, padx=5)

        # Progress bar
        style = ttk.Style()
        style.configure("green.Horizontal.TProgressbar", background='green')
        self.progress = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=600, 
                                      mode='determinate', style="green.Horizontal.TProgressbar")
        self.progress.pack(padx=20, pady=10)

        # Status
        self.status = ttk.Label(self, text="Ready", font=("Arial", 12))
        self.status.pack(padx=20, pady=5)

        # History
        history_frame = ttk.LabelFrame(self, text="Download History")
        history_frame.pack(fill=tk.BOTH, padx=20, pady=10, expand=True)
        history_controls = ttk.Frame(history_frame)
        history_controls.pack(fill=tk.X, padx=5, pady=5)
        clear_history_btn = ttk.Button(history_controls, text="Clear History", command=self.clear_history)
        clear_history_btn.pack(side=tk.RIGHT)
        self.history_listbox = tk.Listbox(history_frame, height=6)
        self.history_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add scrollbar to History listbox
        history_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_listbox.yview)
        self.history_listbox.configure(yscrollcommand=history_scrollbar.set)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add terminal-like output to the GUI
        self.terminal_output = tk.Text(self, height=6, wrap=tk.WORD, state=tk.DISABLED)
        self.terminal_output.pack(fill=tk.BOTH, padx=20, pady=10)

        self.update_history()

    def paste_url(self):
        text = get_clipboard_text()
        self.url_entry.set(text)

    def add_url(self):
        url = self.url_entry.get().strip()
        if url and is_youtube_url(url):
            clean_url = sanitize_youtube_url(url)
            if 'playlist?list=' in clean_url:
                # Clear previous queue for playlists
                self.clear_urls()
                # Show spinner during playlist processing
                self.show_spinner()
                # Extract all video URLs from playlist
                playlist_urls = self.manager.ytdlp_downloader.extract_playlist_urls(clean_url)
                for video_url in playlist_urls:
                    self.urls.append(video_url)
                    self.url_listbox.insert(tk.END, video_url)
                self.status.config(text=f"Added {len(playlist_urls)} videos from playlist")
                self.hide_spinner()
            else:
                self.urls.append(clean_url)
                self.url_listbox.insert(tk.END, clean_url)
            self.url_entry.set("")
            
    def clear_history(self):
        if messagebox.askyesno("Clear History", "Are you sure you want to clear the download history?"):
            self.history.history = []
            self.history.save()
            self.update_history()

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
        self.status.config(text="Preparing downloads...")
        self.progress['value'] = 0
        self.progress['maximum'] = 100
        self.completed_files = 0
        self.total_files = len(self.urls)

        # Show spinner during download preparation
        self.show_spinner()

        def progress_callback(d):
            if d.get('status') == 'downloading':
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes', 0)
                percent = 0
                if total_bytes:
                    percent = downloaded / total_bytes * 100
                # Schedule update in main thread
                self.progress.after(0, lambda: self.progress.configure(value=percent))
                # Limit video name length in the GUI
                MAX_NAME_LENGTH = 50

                # Truncate long video names
                truncated_name = (d.get('filename', '')[:MAX_NAME_LENGTH] + '...') if len(d.get('filename', '')) > MAX_NAME_LENGTH else d.get('filename', '')
                self.status.after(0, lambda: self.status.config(text=f"Downloading: {truncated_name} ({percent:.1f}%) | Completed: {self.completed_files}/{self.total_files}"))
                # Update terminal-like output during download
                self.terminal_output.configure(state=tk.NORMAL)
                self.terminal_output.insert(tk.END, f"Downloading: {d.get('filename', '')} ({percent:.1f}%) | Completed: {self.completed_files}/{self.total_files}\n")
                self.terminal_output.configure(state=tk.DISABLED)
                self.terminal_output.see(tk.END)
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

    # Function to animate spinner
    def animate_spinner(self, frame=0):
        # Update spinner animation to handle empty frames
        if not self.spinner_frames:
            print("Spinner frames are not loaded. Cannot animate spinner.")
            return
        frame = (frame + 1) % len(self.spinner_frames)
        self.spinner_label.configure(image=self.spinner_frames[frame])
        self.after(100, self.animate_spinner, frame)

    # Show spinner
    def show_spinner(self):
        self.spinner_label.pack(side=tk.TOP, pady=10)
        self.animate_spinner()

    # Hide spinner
    def hide_spinner(self):
        self.spinner_label.pack_forget()

    # Define the function to open the downloaded folder
    def open_download_folder(self):
        folder_path = self.save_path.get()
        if os.path.exists(folder_path):
            subprocess.Popen(f'explorer "{folder_path}"', shell=True)
        else:
            messagebox.showerror("Error", "Download folder does not exist.")
