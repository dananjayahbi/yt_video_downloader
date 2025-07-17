"""
Reusable widgets for the YouTube Video Downloader GUI.
"""
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb

class LabeledEntry(ttk.Frame):
    def __init__(self, master, label, **kwargs):
        super().__init__(master)
        self.label = ttk.Label(self, text=label)
        self.label.pack(side=tk.LEFT, padx=(0, 8))
        self.entry = ttk.Entry(self, **kwargs)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def get(self):
        return self.entry.get()

    def set(self, value):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)
