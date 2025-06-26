import requests
import schedule
import time
from plyer import notification
from datetime import datetime
import threading
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import sys
import platform
import tkinter as tk
from tkinter import scrolledtext

if platform.system() == "Windows":
    import winsound

exit_app = False
DELAWARE_FIPS = "42045"  # Delaware County FIPS code

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
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
    else:
        print('\a')

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

                geocode = alert.get('geocode', {})
                fips_list = geocode.get('FIPS6', [])

                if DELAWARE_FIPS in fips_list:
                    full_title = alert['headline']
                    safe_title = full_title[:48]

                    description = alert['description']
                    message = (description[:253] + "...") if len(description) > 256 else description

                    print(f"🔔 ALERT: {full_title}")
                    notification.notify(
                        title=f"Weather Alert: {safe_title}",
                        message=message,
                        timeout=15
                    )
                    play_alert_sound()
                    show_alert_popup(full_title, description)
                    time.sleep(2)
                else:
                    print(f"[{datetime.now()}] Skipped alert not for Delaware County (FIPS filter).")
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
    draw.ellipse((16, 16, 48, 48), fill=(255, 215, 0))
    return image

def setup_tray():
    icon_image = create_icon()
    menu = Menu(MenuItem('Quit', quit_app))
    tray_icon = Icon("Weather Alert", icon_image, "Delaware Alerts", menu)
    tray_icon.run()

def main():
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.daemon = True
    schedule_thread.start()
    setup_tray()

if __name__ == "__main__":
    main()
