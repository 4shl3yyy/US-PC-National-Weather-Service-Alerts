import os
import sys
import requests
import schedule
import time
import threading
from datetime import datetime
from plyer import notification
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import tkinter as tk
from tkinter import scrolledtext
import platform

# Allegany County identifiers
ALLEGANY_FIPS = "42003"
ALLEGANY_ZONE = "PAZ003"

exit_app = False

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

def check_weather_alerts():
    print(f"[{datetime.now()}] Checking for alerts...")
    url = "https://api.weather.gov/alerts/active"
    headers = {'User-Agent': 'weather-alert-app'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data['features']:
            print(f"[{datetime.now()}] {len(data['features'])} total alert(s) found.")
            for alert_feature in data['features']:
                alert = alert_feature['properties']

                # Filter to only alerts from NWS Pittsburgh
                sender = alert.get("sender", "").lower()
                sender_name = alert.get("senderName", "").lower()
                if ("pbg" not in sender) and ("pittsburgh" not in sender_name):
                    print(f"[{datetime.now()}] Skipped alert not from NWS Pittsburgh (sender: {sender_name})")
                    continue

                geocode = alert.get('geocode', {})
                fips_list = geocode.get('FIPS6', []) or []
                zone_list = geocode.get('UGC', []) or []
                affected_zones = alert.get('affectedZones', []) or []

                headline = alert.get('headline') or ''
                description = alert.get('description') or ''
                combined_text = (headline + description).lower()

                print(f"Alert headline: {headline}")
                print(f"Sender: {sender_name}")
                print(f"FIPS: {fips_list}")
                print(f"Zones: {zone_list}")
                print(f"Affected Zones: {affected_zones}")

                if (ALLEGANY_FIPS in fips_list or 
                    ALLEGANY_ZONE in zone_list or
                    any(ALLEGANY_ZONE in zone for zone in affected_zones) or
                    "allegany" in combined_text):

                    full_title = headline
                    safe_title = full_title[:48]
                    message_text = description[:253] + "..." if len(description) > 256 else description

                    print(f"🔔 ALERT: {full_title}")
                    notification.notify(
                        title=f"Weather Alert: {safe_title}",
                        message=message_text,
                        timeout=15
                    )
                    show_alert_popup(full_title, description)
                    time.sleep(2)
                else:
                    print(f"[{datetime.now()}] Skipped alert not specific to Allegany County.")
        else:
            print(f"[{datetime.now()}] No active alerts.")
    except Exception as e:
        print(f"[{datetime.now()}] Error: {e}")

def run_schedule():
    check_weather_alerts()
    schedule.every(10).minutes.do(check_weather_alerts)
    while not exit_app:
        schedule.run_pending()
        time.sleep(1)

def quit_app(icon, item):
    global exit_app
    print("Exiting app...")
    exit_app = True
    icon.stop()
    sys.exit(0)

def create_icon():
    icon_size = 64
    image = Image.new('RGB', (icon_size, icon_size), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((16, 16, 48, 48), fill=(255, 0, 0))  # Red circle icon
    return image

def setup_tray():
    icon_image = create_icon()
    menu = Menu(MenuItem('Quit', quit_app))
    tray_icon = Icon("Weather Alert", icon_image, "Allegany Weather Alerts", menu)
    tray_icon.run()

def main():
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.daemon = True
    schedule_thread.start()
    setup_tray()

if __name__ == "__main__":
    main()
