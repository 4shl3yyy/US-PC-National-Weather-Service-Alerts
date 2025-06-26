import requests
import schedule
import time
from plyer import notification
from datetime import datetime
import threading
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import sys
import os
import tkinter as tk
from tkinter import scrolledtext
import platform

if platform.system() == "Windows":
    import winsound

exit_app = False

ALLEGHENY_FIPS = "42003"     # FIPS code for Allegheny County, PA
ALLEGHENY_ZONE = "PAZ021"    # Forecast zone for Allegheny County, PA

def show_alert_popup(title, full_text):
    def popup():
        root = tk.Tk()
        root.title(title)
        root.geometry("500x300")
        root.attributes('-topmost', True)

        text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD)
        text_area.pack(expand=True, fill='both')
        text_area.insert(tk.END, full_text)
        text_area.configure(state='disabled')

        root.mainloop()

    threading.Thread(target=popup, daemon=True).start()

def play_alert_sound():
    if platform.system() == "Windows":
