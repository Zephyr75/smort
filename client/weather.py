"""
weather_lcd.py — Fetch weather and render into a 20×4 LCD display

No API key needed — uses wttr.in (free, no signup)

Usage:
    python weather_lcd.py                   # auto-detect location by IP
    python weather_lcd.py Paris
    python weather_lcd.py "New York" -t E   # 3-day forecast template
    python weather_lcd.py Tokyo -t F        # boxed dashboard template
    python weather_lcd.py London -t all     # show all three templates
    python weather_lcd.py Berlin --ascii    # ASCII-only (real LCD safe)
"""

import json
import argparse
import urllib.request
import urllib.parse
from datetime import datetime

W = 20  # display width in characters

# ── Weather codes → (description, unicode icon, ascii icon) ─────────────────
WX = {
    113: ("Sunny",           "*", "*"),
    116: ("Partly cloudy",   "%", "%"),
    119: ("Cloudy",          "o", "o"),
    122: ("Overcast",        "o", "o"),
    143: ("Mist",            "-", "-"),
    176: ("Light rain",      "/", "/"),
    179: ("Light sleet",     "x", "x"),
    182: ("Sleet",           "x", "x"),
    200: ("Thunderstorm",    "!", "!"),
    227: ("Blowing snow",    "+", "+"),
    230: ("Blizzard",        "+", "+"),
    248: ("Fog",             "-", "-"),
    260: ("Freezing fog",    "-", "-"),
    263: ("Light drizzle",   ".", "."),
    266: ("Drizzle",         ".", "."),
    281: ("Frz drizzle",     ".", "."),
    293: ("Light rain",      "/", "/"),
    296: ("Rain",            "/", "/"),
    299: ("Heavy rain",      "//","//"),
    302: ("Heavy rain",      "//","//"),
    305: ("Heavy rain",      "//","//"),
    320: ("Light snow",      "+", "+"),
    323: ("Light snow",      "+", "+"),
    326: ("Snow",            "+", "+"),
    329: ("Heavy snow",      "++","++"),
    353: ("Light rain",      "/", "/"),
    356: ("Heavy rain",      "//","//"),
    368: ("Light snow",      "+", "+"),
    386: ("Thunderstorm",    "!", "!"),
    389: ("Heavy thunder",   "!!", "!!"),
}

def wx(code: int, ascii_mode: bool) -> tuple[str, str]:
    entry = WX.get(code, ("Unknown", "?", "?"))
    return entry[0], (entry[2] if ascii_mode else entry[1])


# ── Fetch ────────────────────────────────────────────────────────────────────

def fetch(location: str) -> dict:
    loc = urllib.parse.quote(location) if location else ""
    url = f"https://wttr.in/{loc}?format=j1"
    req = urllib.request.Request(url, headers={"User-Agent": "weather_lcd/1.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())


# ── Parse ────────────────────────────────────────────────────────────────────

def parse(data: dict, ascii_mode: bool) -> dict:
    cur  = data["current_condition"][0]
    area = data["nearest_area"][0]
    code = int(cur["weatherCode"])
    desc, icon = wx(code, ascii_mode)

    city    = area["areaName"][0]["value"]
    country = area["country"][0]["value"]

    days = []
    for d in data["weather"][:3]:
        dt     = datetime.strptime(d["date"], "%Y-%m-%d")
        dc, di = wx(int(d["hourly"][4]["weatherCode"]), ascii_mode)
        days.append({
            "label":  dt.strftime("%a").upper(),   # "SAT"
            "date":   dt.strftime("%d %b"),         # "22 Mar"
            "max_c":  int(d["maxtempC"]),
            "min_c":  int(d["mintempC"]),
            "desc":   dc,
            "icon":   di,
        })

    return {
        "city":    city,
        "country": country,
        "temp_c":  int(cur["temp_C"]),
        "feels_c": int(cur["FeelsLikeC"]),
        "hum":     int(cur["humidity"]),
        "wind_k":  int(cur["windspeedKmph"]),
        "wind_d":  cur["winddir16Point"],          # "SW", "NNE", etc.
        "pres":    int(cur["pressure"]),
        "uv":      int(cur["uvIndex"]),
        "vis":     int(cur["visibility"]),
        "desc":    desc,
        "icon":    icon,
        "days":    days,
    }


# ── Row builder (guarantees exactly W chars) ─────────────────────────────────

def row(left: str, right: str = "", width: int = W) -> str:
    """Left-align `left`, right-align `right`, pad middle with spaces."""
    inner = left + right.rjust(width - len(left))
    return inner[:width].ljust(width)   # hard-clip + pad if needed

def centre(text: str, width: int = W) -> str:
    return text[:width].center(width)

def fill(text: str, width: int = W) -> str:
    return text[:width].ljust(width)


# ── Templates ────────────────────────────────────────────────────────────────

def template_D(w: dict) -> list[str]:
    """
    Template D — Current conditions
    ┌────────────────────┐
    │Paris          * 18°│
    │Partly Cloudy       │
    │Hum:72%   Wind:SW12 │
    │Feels:15°  Pres:1013│
    └────────────────────┘
    """
    city  = w["city"][:11]
    temp  = f"{w['icon']} {w['temp_c']}\xb0"          # "* 18°"
    desc  = w["desc"][:W]
    hum   = f"Hum:{w['hum']}%"
    wind  = f"Wind:{w['wind_d']}{w['wind_k']}"
    feels = f"Feels:{w['feels_c']}\xb0"
    pres  = f"P:{w['pres']}"

    return [
        row(city, temp),
        fill(desc),
        row(hum, wind),
        row(feels, pres),
    ]


def template_E(w: dict) -> list[str]:
    """
    Template E — 3-day forecast
    ┌────────────────────┐
    │ SAT    SUN    MON  │
    │ *18°   o16°   +12° │
    │────────────────────│
    │Hum:72%   Wind:SW12 │
    └────────────────────┘
    """
    days = w["days"]

    def col(d: dict) -> str:
        # Each day gets a 6-char slot: label centred, then icon+temp
        return d["label"].center(6), \
               (d["icon"] + str(d["max_c"]) + "\xb0").center(6)

    labels = []
    temps  = []
    for d in days[:3]:
        lb, tp = col(d)
        labels.append(lb)
        temps.append(tp)

    # pad to 3 cols if fewer than 3 days returned
    while len(labels) < 3:
        labels.append("      ")
        temps.append("      ")

    hum  = f"Hum:{w['hum']}%"
    wind = f"Wind:{w['wind_d']}{w['wind_k']}"

    return [
        (" ".join(labels) + " ")[:W],           # row 1: day names
        (" ".join(temps) + " ")[:W],             # row 2: icon+max temp
        "\u2500" * W,                            # row 3: horizontal rule ──────
        row(hum, wind),                          # row 4: current meta
    ]


def template_F(w: dict) -> list[str]:
    """
    Template F — Boxed dashboard
    ╔═ PARIS * 18°C ════╗
    ║Partly Cloudy      ║
    ║Hum:72%  Wind:SW12 ║
    ╚22 Mar     Feels:15╝
    """
    city   = w["city"][:6].upper()
    temp   = f"{w['icon']} {w['temp_c']}\xb0C"        # "* 18°C"
    title  = f" {city} {temp} "                        # " PARIS * 18°C "

    # pad title to exactly W-2 chars with ═, then wrap in corners
    inner_w = W - 2
    if len(title) < inner_w:
        title = title + "\u2550" * (inner_w - len(title))
    title = title[:inner_w]
    r1 = "\u2554" + title + "\u2557"                   # ╔...╗

    desc   = fill(w["desc"], inner_w)
    r2     = "\u2551" + desc + "\u2551"                # ║...║

    hum    = f"Hum:{w['hum']}%"
    wind   = f"Wind:{w['wind_d']}{w['wind_k']}"
    mid    = row(hum, wind, inner_w)
    r3     = "\u2551" + mid + "\u2551"                 # ║...║

    date   = w["days"][0]["date"] if w["days"] else ""
    feels  = f"Feels:{w['feels_c']}\xb0"
    foot   = row(date, feels, inner_w)
    r4     = "\u255a" + foot + "\u255d"                # ╚...╝

    return [r1, r2, r3, r4]


# ── Render to terminal ───────────────────────────────────────────────────────

TEMPLATE_NAMES = {
    "D": ("Current conditions", template_D),
    "E": ("3-day forecast",     template_E),
    "F": ("Boxed dashboard",    template_F),
}

def render(rows: list[str], label: str) -> None:
    top    = "\u250c" + "\u2500" * W + "\u2510"
    bottom = "\u2514" + "\u2500" * W + "\u2518"
    side   = "\u2502"

    print(f"\n  {label}")
    print("  " + top)
    for r in rows:
        # Ensure exactly W display chars (strip/pad)
        r = r[:W].ljust(W)
        print(f"  {side}{r}{side}")
    print("  " + bottom)


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch weather and display on a 20×4 LCD layout"
    )
    parser.add_argument("location", nargs="?", default="",
                        help="City name, or empty for IP-detected location")
    parser.add_argument("-t", "--template", default="D",
                        choices=["D", "E", "F", "all"],
                        help="D=current, E=3-day, F=boxed, all=show all three")
    parser.add_argument("--ascii", action="store_true",
                        help="Use ASCII-only icons (safe for physical LCD hardware)")
    args = parser.parse_args()

    print(f"Fetching: {args.location or '(auto-detect)'} …")
    data    = fetch(args.location)
    weather = parse(data, args.ascii)

    targets = (
        list(TEMPLATE_NAMES.keys()) if args.template == "all"
        else [args.template]
    )

    for key in targets:
        name, fn = TEMPLATE_NAMES[key]
        rows = fn(weather)
        render(rows, f"Template {key} — {name}")

    # Also print a raw rows dump so you can paste directly into your device code
    if len(targets) == 1:
        key  = targets[0]
        rows = TEMPLATE_NAMES[key][1](weather)
        print(f"\n  Raw rows (copy into your device code):")
        for i, r in enumerate(rows):
            print(f"    row[{i}] = {r!r}")


if __name__ == "__main__":
    main()
