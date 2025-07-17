"""
App GUI runner for YouTube Video Downloader.
"""
import ttkbootstrap as tb
import tkinter as tk
from .main_window import MainWindow

def run_app():
    root = tb.Window(themename="darkly")
    root.title("YouTube Video Downloader")
    root.geometry("900x600")
    app = MainWindow(root)
    root.mainloop()
