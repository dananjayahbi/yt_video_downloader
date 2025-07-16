"""
Clipboard integration utility for YouTube Video Downloader.
"""
import tkinter as tk

def get_clipboard_text():
    root = tk.Tk()
    root.withdraw()
    try:
        text = root.clipboard_get()
    except tk.TclError:
        text = ''
    root.destroy()
    return text
