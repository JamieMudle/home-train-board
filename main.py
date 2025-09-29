import network
import time
import urequests
import json

from CONFIG import APP_KEY, LINE, STATION_ID # must be defined in CONFIG.py and on same pico board
from WIFI_CONFIG import SSID, PSK # must be defined in WIFI_CONFIG.py and on same pico board
from interstate75 import Interstate75, DISPLAY_INTERSTATE75_128X64
from picographics import PicoGraphics

# Small delay to allow for safe reloading of modules and boot
time.sleep(1)

# ==== Wi-Fi & API Setup ====
APP_KEY = APP_KEY
LINE = LINE
STATION_ID = STATION_ID 

# ==== Display Setup ====
i75 = Interstate75(display=DISPLAY_INTERSTATE75_128X64)
graphics = i75.display

width = i75.width
height = i75.height

# ==== Pens (Colors) ====
WHITE = graphics.create_pen(255, 255, 255)
BLACK = graphics.create_pen(0, 0, 0)
RED = graphics.create_pen(217, 4, 43)
GREEN = graphics.create_pen(15, 140, 59)
BLUE = graphics.create_pen(0, 0, 255)
ORANGE = graphics.create_pen(242, 156, 80)
YELLOW = graphics.create_pen(242, 193, 46)
MAGENTA = graphics.create_pen(255, 0, 255)
HEADER = graphics.create_pen(140, 67, 3)
TEXT = graphics.create_pen(217, 152, 30)
GRAY = graphics.create_pen(128, 144, 166)

# ==== Utility Functions ====

def legal_notice():
    messages = [
    "Powered by TfL Open Data",
    "Contains OS data © Crown copyright and database rights 2016",
    "Contains Geomni UK Map data © and database rights [2019]",
    ]
    for message in messages:
        graphics.set_pen(BLACK)
        graphics.clear()
        graphics.set_pen(TEXT)
        graphics.text(message, 0, 14, width, scale=1)
        i75.update(graphics)
        time.sleep(5)

def get_disruptions():
    url = f"https://api.tfl.gov.uk/Line/{LINE}/Disruption?app_key={APP_KEY}" # set your own line and app_key in CONFIG.py
    res = urequests.get(url)
    data = res.json()
    res.close()

    if not data:
        return "Good Service", GREEN

    closure = data[0].get("closureText", "").strip().lower()

    if closure == "severedelays":
        return "Severe Delays", RED
    elif closure == "minordelays":
        return "Minor Delays", YELLOW
    elif closure == "partsuspended":
        return "Part Suspended", BLUE
    else:
        return closure.title(), MAGENTA

def get_arrivals():
    url =  f"https://api.tfl.gov.uk/StopPoint/{STATION_ID}/Arrivals?app_key={APP_KEY}" # set your own station_id and app_key in CONFIG.py
    res = urequests.get(url)
    data = res.json()
    res.close()
    data.sort(key=lambda x: x["timeToStation"])
    return data

def show_text(lines, color=WHITE):
    graphics.set_pen(BLACK)
    graphics.clear()
    graphics.set_pen(color)

    y = 0
    for line in lines:
        graphics.text(line, 0, y, width, scale=1)
        y += 12

    i75.update(graphics)

def show_arrivals(arrivals, status_color):
    graphics.set_pen(BLACK)
    graphics.clear()

    # Draw status square
    graphics.set_pen(status_color)
    graphics.rectangle(0, 0, 8, 8)

    # Draw header
    graphics.set_font("bitmap8")
    graphics.set_pen(HEADER)
    graphics.text("Woodford Departures", 12, 0, width, scale=1)

    # Draw arrivals
    graphics.set_font("bitmap6")
    graphics.set_pen(TEXT)

    y = 14
    for item in arrivals:
        words = item["destinationName"].split()
        filtered = " ".join(w for w in words if w.lower() not in ["underground", "station"])
        dest = " ".join(filtered.split()[:2])
        mins = item["timeToStation"] // 60
        time_text = "DUE" if mins == 0 else f"{mins}m"

        graphics.text(dest, 0, y, width, scale=1)
        graphics.text(time_text, 100, y, width, scale=1)
        y += 12
        
    i75.update(graphics)

# ==== Wi-Fi Connect Screen ====

graphics.set_pen(BLACK)
graphics.clear()
graphics.set_pen(MAGENTA)
graphics.set_font("bitmap6")
graphics.text("Connecting...", 0, 20, width, scale=1)
i75.update(graphics)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PSK)

while not wlan.isconnected():
    time.sleep(1)

graphics.set_pen(BLACK)
graphics.clear()
graphics.set_pen(GREEN)
graphics.text("Connected!", 0, 20, width, scale=1)
i75.update(graphics)
time.sleep(1)

# ==== Main Loop ====

last_arrivals = []
legal_time = 0
scroll_index = 0
max_visible = 4
scroll_delay = 5
fetch_interval = 30  # seconds between API calls to avoid rate limiting
scroll_cycles = 0
last_fetch = time.time() - fetch_interval  # force immediate first fetch

while True:
    current_time = time.time()

    # Fetch new data only every `fetch_interval` seconds
    if current_time - last_fetch >= fetch_interval:
        try:
            status_text, status_color = get_disruptions()
            arrivals = get_arrivals()

            if arrivals:
                last_arrivals = arrivals
                scroll_cycles = 0
            elif last_arrivals:
                scroll_cycles += 1
                if scroll_cycles >= 6:
                    last_arrivals = []
                    show_text(["No trains", "Check again soon"], color=RED)
                    time.sleep(scroll_delay)
                    continue
            else:
                show_text(["No trains", "Check again soon"], color=RED)
                time.sleep(scroll_delay)
                continue

            last_fetch = current_time

        except Exception as e:
            print("Error:", e)
            show_text(["API ERROR", str(e)], color=RED)
            time.sleep(scroll_delay)
            continue

    # Scroll display from last_arrivals regardless of fetch timing
    if last_arrivals:
        start = scroll_index
        end = scroll_index + max_visible
        visible_arrivals = last_arrivals[start:end]
        show_arrivals(visible_arrivals, status_color)

        scroll_index += max_visible
        if scroll_index >= len(last_arrivals):
            scroll_index = 0

    time.sleep(scroll_delay)
    
    legal_time += 1
    
    if legal_time >= 720:
        legal_notice()
        legal_time = 0
    else:
        continue
    



