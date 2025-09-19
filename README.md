# home-train-board
A tiny MicroPython app for a Raspberry Pi Pico W + Pimoroni Interstate 75 128×64 display that shows live TfL line status and upcoming arrivals for a chosen station. It connects to Wi-Fi, pulls data from TfL’s public API, and scrolls departures on the LED matrix.

## What you'll see
- A coloured square which indicates service status for your chosen line + header (hardcoded for your station name)
- Up to 4 arrivals at a time, more than 4 and the app auto-scrolls through the list
- Times shown as DUE or Xm

### Status colours
- **Green** = good service
- **Yellow** = minor delays
- **Red** = severe delays
- **Blue** = part suspended
- **Magenta** = unknown/anything else returned by TfL (closureText) 

## Hardware
- Raspberry Pi Pico W or Pimoroni Interstate 75
- 128×64 LED dot matrix board (can do any size but this is the one used here)
- USB cable for power/flashing/loading the app onto the board

## Files
Place these on the boards drive using Thonny (or whatever IDE/Method you're comfortable with)
``` bash
/main.py               # main app file
/CONFIG.py             # your TfL/API config (template included)
/WIFI_CONFIG.py        # your Wi-Fi credentials (template included)
```

## How it works
- Connects to Wi-Fi, shows "Connecting" in Magenta for connecting to wifi and then "Connected!" in green once connection is established. Then moves on.

- Fetches line status from
https://api.tfl.gov.uk/Line/{LINE}/Disruption?app_key={APP_KEY}

- Fetches arrivals (inbound) from
https://api.tfl.gov.uk/Line/{LINE}/Arrivals/{STATION_ID}?direction=inbound&app_key={APP_KEY}

- Sorts by timeToStation, displays up to 4 entries at once, and scrolls.

- Throttles API calls with fetch_interval = 30 seconds (tweakable).

- Falls back to the last known arrivals list if a fetch fails.

- Shows an API ERROR screen on exceptions.

### Key Tweakable Variables
``` python
max_visible   = 4   # arrivals shown per page
scroll_delay  = 5   # seconds between scroll updates
fetch_interval = 30 # seconds between API requests
```
The header text is currently hard-coded as "Woodford Departures"—change it in show_arrivals() to suit your station.

The URL uses inbound for arrivals (trains going into london) if you want to check trains heading outwards change that to outbound in the URL variable

## Setup
1. Flash firmware: load Pimoroni’s MicroPython UF2 onto the Pico W. If using the interstate 75w use the appropriate firmware

2. Copy files: save main.py, CONFIG.py, and WIFI_CONFIG.py to the Pico.

3. Edit config: put your APP_KEY, LINE, and STATION_ID in CONFIG.py; Wi-Fi in WIFI_CONFIG.py.

4. Reboot the Pico W (power cycle). The display should show “Connecting…”, then the departures.

Tip: If you don’t want the script to auto-run, name it something else and run it from the REPL. For auto-run, name it main.py.

## Finding values for CONFIG.py
- LINE is the TfL line ID (lowercase), e.g. central, jubilee, victoria.

- STATION_ID is the station’s StopPoint/Naptan ID, e.g. 940GZZLUWOF (Woodford).
Search the TfL API browser for your station or inspect another arrivals response to discover it.

## Troubleshooting

- **Nothing shows / stuck on “Connecting…”**
Double-check SSID/PSK. Ensure your Wi-Fi is 2.4 GHz and the Pico W is in range.

- **API ERROR**
  1. Wrong APP_KEY, LINE, or STATION_ID
  2. Temporary network issue (the app will retry)
  3. TfL rate limiting (you can increase fetch_interval)

- **Weird destination names**
The code strips “Underground”/“Station” and truncates to two words. Adjust the filtering in show_arrivals() if you prefer full names.

- **Outbound vs inbound**
The arrivals URL uses direction=inbound. Change or remove the direction parameter for your use case.

## Make it yours
- Change fonts 
- Swap colours or add themes for different statuses.
- Show time of last update in a footer.
- Add a button to toggle inbound/outbound.
- Add a button to toggle different lines/displays

## Licenses
For the code provided here:

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

For TFL Licences (if using the TFL API) please see https://tfl.gov.uk/corporate/terms-and-conditions/transport-data-service

## Acknowledgements
- TFL Unified API
- Interstate 75W & PicoGraphics