import json
import urllib.request
import urllib.parse
import sys

WIDTH = 20

WX = {
    113: ("Sunny", "*"),        116: ("Partly cloudy", "%"),
    119: ("Cloudy", "o"),       122: ("Overcast", "o"),
    143: ("Mist", "-"),         176: ("Light rain", "/"),
    200: ("Thunderstorm", "!"), 227: ("Blowing snow", "+"),
    248: ("Fog", "-"),          263: ("Light drizzle", "."),
    266: ("Drizzle", "."),      296: ("Rain", "/"),
    299: ("Heavy rain", "//"),  320: ("Light snow", "+"),
    326: ("Snow", "+"),         386: ("Thunderstorm", "!"),
}

def fetch(city):
    url = f"https://wttr.in/{urllib.parse.quote(city)}?format=j1"
    req = urllib.request.Request(url, headers={"User-Agent": "weather_lcd/1.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())

def row(left, right):
    return (left + right.rjust(WIDTH - len(left)))[:WIDTH].ljust(WIDTH)

def get_weather(city):
    data = fetch(city)
    cur  = data["current_condition"][0]
    code = int(cur["weatherCode"])
    desc, icon = WX.get(code, ("Unknown", "?"))

    r1 = row(city[:14], f"{icon} {cur['temp_C']}\xb0")
    r2 = desc[:20].ljust(20)
    r3 = row(f"Hum:{cur['humidity']}%", f"Wind:{cur['winddir16Point']}{cur['windspeedKmph']}")
    r4 = row(f"Feels:{cur['FeelsLikeC']}°", f"UV:{cur['uvIndex']}")

    return [r1, r2, r3, r4]


if __name__ == "__main__":
    city = sys.argv[1] if len(sys.argv) > 1 else "Paris"
    for line in get_weather(city):
        print(line)
