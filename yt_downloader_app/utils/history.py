"""
Download history management for YouTube Video Downloader.
"""
import json
import os

HISTORY_FILE = os.path.join(os.path.dirname(__file__), '..', 'assets', 'history.json')

class HistoryManager:
    def __init__(self):
        self.history = []
        self.load()

    def load(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
        else:
            self.history = []

    def add(self, entry):
        self.history.append(entry)
        self.save()

    def save(self):
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2)

    def get_all(self):
        return self.history
