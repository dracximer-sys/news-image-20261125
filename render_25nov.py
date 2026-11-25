#!/usr/bin/env python3
"""Render the 25 November 2026 front page for the make.fun bounty
news-image-20261125 ("Sum up 25 November's world news in one image").

Build-time only: renders a 1024x1024 newspaper front page to entry.png
using Pillow. No network calls. Deterministic output: no random values,
no timestamps, fixed text and fixed geometry.

Data: research/stories-20261125.md (40 verified stories, Wednesday
25 November 2026). Facts (names, numbers, places, outcomes) are kept
identical to that file; only the wording of titles/summaries is mine.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 24  # side margin
PAPER = (251, 248, 241)
INK = (17, 17, 17)
RED = (185, 28, 28)
NAVY = (30, 58, 95)
SEA = (214, 228, 240)
LAND = (232, 224, 204)
GREY = (90, 90, 90)
LINE = (210, 205, 195)
BODY = (40, 40, 40)

FONT_DIR = "/usr/share/fonts/truetype/liberation/"


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


SERIF_B = lambda s: font("LiberationSerif-Bold.ttf", s)
SERIF = lambda s: font("LiberationSerif-Regular.ttf", s)
SANS = lambda s: font("LiberationSans-Regular.ttf", s)
SANS_B = lambda s: font("LiberationSans-Bold.ttf", s)


def wrap(text, fnt, width):
    """Split text into lines that fit `width` pixels with font `fnt`."""
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = (cur + " " + word).strip()
        if fnt.getlength(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, width, fill, leading):
    """Draw wrapped text; return the y just below the last line."""
    for line in wrap(text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def centred(draw, cx, y, text, fnt, fill):
    draw.text((cx - fnt.getlength(text) / 2, y), text, font=fnt, fill=fill)


# ---------------------------------------------------------------- data
# Headline stories 1-3: (number, title, summary, illustration label)
TOP_STORIES = [
    (
        "1",
        "TANKERS HIT MINES IN HORMUZ",
        "Two oil tankers struck naval mines, exploded and caught fire "
        "in the Strait of Hormuz early on Wednesday. Brent crude traded "
        "around $91-92 a barrel.",
        "STRAIT OF HORMUZ",
    ),
    (
        "2",
        "HOUTHIS STRIKE RAS TANURA REFINERY",
        "Yemen's Houthis say they attacked Saudi Arabia's Ras Tanura "
        "refinery, the kingdom's largest at 550,000 barrels a day, "
        "causing fires.",
        "RAS TANURA",
    ),
    (
        "3",
        "SHENZHOU-24 PUTS FIRST PAKISTANI IN ORBIT",
        "Shenzhou-24 launches from Jiuquan and docks with Tiangong "
        "after a 3.5-hour flight, carrying Tang Hongbo, Wu Yi and "
        "Muhammad Zeeshan Ali, 40 — the first Pakistani in orbit.",
        "JIUQUAN",
    ),
]

# Stories 4-40, region-ordered: (number, region, title)
GRID = [
    (4, "EUROPE", "Ukrainian drones hit two Rosneft refineries in Samara"),
    (5, "EUROPE", "Russian strike kills two in Ukraine's Odesa region"),
    (6, "EUROPE", "At least 490,334 Russian soldiers dead since 2022, BBC finds"),
    (7, "EUROPE", "Sarkozy and Bruni ordered to stand trial in France"),
    (8, "EUROPE", "French bond yields hit highest level since 2002"),
    (9, "EUROPE", "Poland pushes for permanent US military presence"),
    (10, "MIDDLE EAST", "Israel kills Hamas colonel Abuelouf in Gaza City strike"),
    (11, "MIDDLE EAST", "Iran says it downed two US drones over Hormuz"),
    (12, "MIDDLE EAST", "Container ship targeted near Hormuz, IRGC says"),
    (13, "AMERICAS", "Colombia frees hostages after Cartagena supermarket siege"),
    (14, "AMERICAS", "Trump administration proposes tariffs on 14 trading partners"),
    (15, "AMERICAS", "Democrats win House majority of at least 259 seats"),
    (16, "AMERICAS", "Argentina enters technical recession"),
    (17, "AMERICAS", "WHO: Cuban life expectancy falls for first time since 1950"),
    (18, "ASIA", "Australia and Solomon Islands sign historic defence treaty"),
    (19, "ASIA", "Three bodies recovered from flooded gold mine in Bogor"),
    (20, "ASIA", "Australia's inflation jumps to 4.9%"),
    (21, "ASIA", "China investigates Shanghai party chief Chen Jining"),
    (22, "ASIA", "North Korea expels Swiss diplomat, closes office"),
    (23, "AFRICA", "RSF drone strikes kill 19 civilians in Sudan's Blue Nile"),
    (24, "AFRICA", "Kenyan cult leader Mackenzie convicted of child cruelty"),
    (25, "AFRICA", "Nigeria seizes $227M of methamphetamine, arrests five Mexicans"),
    (26, "AFRICA", "Ramaphosa wins court bid to set aside Farmgate report"),
    (27, "AFRICA", "Africa could cut debt by borrowing for investment, OECD-AU say"),
    (28, "TECH & SPACE", "AI safety doubts inside Anthropic and OpenAI, Axios reports"),
    (29, "TECH & SPACE", "Nvidia shares fall again as lawmakers question Trump's role"),
    (30, "TECH & SPACE", "China's Qianfan satellite constellation advances"),
    (31, "ECONOMY", "South Korea's KOSPI plunges 6.16% in a single session"),
    (32, "ECONOMY", "US economy grows 4.3% in Q3, revised up from 3.4%"),
    (33, "ECONOMY", "Dow dives about 700 points as Nvidia sell-off deepens"),
    (34, "ECONOMY", "Deere misses profit forecast as farm equipment sales fall 15%"),
    (35, "ECONOMY", "EasyJet annual profit falls 89% after fuel cost hit"),
    (36, "SPORT & CULTURE", "World Chess Championship Game 2 under way in Geneva"),
    (37, "SPORT & CULTURE", "Champions League Matchday 5 continues with nine fixtures"),
    (38, "SPORT & CULTURE", "Toronto Blue Jays agree deal with pitcher Kaima Taira"),
    (39, "CLIMATE", 'Pope Leo XIV calls COP31 failure "troubling"'),
    (40, "CLIMATE", "Nepal leaves COP31 without the flood aid it sought"),
]

REGION_ORDER = [
    "EUROPE", "MIDDLE EAST", "AMERICAS", "ASIA", "AFRICA",
    "TECH & SPACE", "ECONOMY", "SPORT & CULTURE", "CLIMATE",
]

# The day in numbers: (big figure, label)
NUMBERS = [
    ("2", "oil tankers hit by naval mines in the Strait of Hormuz"),
    ("550,000", "barrels a day of capacity at the Ras Tanura refinery"),
    ("-6.16%", "KOSPI plunge in a single session"),
    ("4.3%", "US third-quarter GDP growth, revised up from 3.4%"),
    ("490,334", "Russian soldiers dead since 2022, per BBC analysis"),
    ("$227M", "methamphetamine seized by Nigeria's anti-drug agency"),
]

# Map pins: (lat, lon, label for the key)
PINS = [
    (26.50, 56.25, "Strait of Hormuz — tankers hit mines"),
    (26.65, 50.06, "Ras Tanura — Houthi refinery attack"),
    (40.96, 100.29, "Jiuquan — Shenzhou-24 launch"),
    (53.16, 48.47, "Syzran — refineries hit"),
    (31.50, 34.47, "Gaza City — Abuelouf strike"),
    (10.39, -75.51, "Cartagena — hostages freed"),
    (-35.28, 149.13, "Canberra — Solomons treaty"),
    (-6.59, 106.79, "Bogor — flooded gold mine"),
    (11.76, 34.35, "Damazin — RSF drone strikes"),
    (37.57, 126.98, "Seoul — KOSPI plunge"),
    (46.20, 6.14, "Geneva — Chess Championship Game 2"),
]

DATE_CHECK_BODY = (
    "Not 25 November, so left out: IRGC claim that THREE tankers hit mines "
    "(24 Nov) · Houthi drone hits the PIF Tower in Riyadh, wounding 11 "
    "(24 Nov) · Dow closes above 50,000 for the first time (24 Nov) · "
    "Nvidia shares fall 5.9%, wiping ~$233bn (24 Nov) · COP31 collapse in "
    "Antalya (22 Nov) · ICJ finds Myanmar committed genocide against the "
    "Rohingya (19 Nov) · World Chess Championship Game 1 ends in a draw "
    "(24 Nov) · Huawei found guilty on 10 of 12 counts (24 Nov)."
)

SOURCES = (
    "Sources: Reuters · AP · CNN · BBC · Al Jazeera · The New York Times · "
    "Le Monde · UN News · Euronews · AFP · USA Today · Yonhap · Xinhua · "
    "BEA · pm.gov.au · DFAT · ChessBase · FIDE · UEFA · Investor's Business "
    "Daily · The Hindu BusinessLine · Korea JoongAng Daily · AAP · "
    "FrontPages.eu · The Munich Eye · The Diplomat · Axios · Grist · "
    "One Turn · The Daily Edition · Just Security. "
    "All stories from Wednesday 25 Nov 2026. Built by @drac-ximer."
)

# Continent outlines (lon, lat) — drawn as polygons, equirectangular.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
     (-80, 73), (-70, 62), (-55, 52), (-60, 46), (-70, 42), (-75, 35),
     (-80, 26), (-85, 20), (-90, 14), (-95, 16), (-100, 20), (-105, 22),
     (-110, 28), (-115, 32), (-120, 34), (-125, 40), (-125, 48),
     (-135, 58), (-150, 60), (-165, 60)],
    [(-55, 60), (-45, 60), (-40, 64), (-30, 68), (-25, 70), (-30, 76),
     (-45, 76), (-58, 70), (-60, 64)],
    [(-80, 10), (-75, 12), (-70, 12), (-60, 8), (-50, 4), (-45, 0),
     (-40, -5), (-35, -8), (-40, -15), (-45, -22), (-50, -28), (-55, -35),
     (-60, -40), (-65, -45), (-70, -52), (-73, -45), (-75, -35),
     (-78, -25), (-80, -15), (-82, -5), (-80, 5)],
    [(-17, 15), (-15, 25), (-10, 30), (-5, 35), (0, 36), (10, 37),
     (15, 32), (20, 32), (30, 31), (35, 28), (40, 20), (43, 12), (48, 10),
     (51, 12), (45, 5), (40, -2), (38, -10), (35, -18), (32, -25),
     (28, -32), (20, -35), (15, -30), (12, -18), (10, -5), (8, 4), (0, 5),
     (-8, 5), (-15, 10)],
    [(-10, 36), (-9, 43), (-2, 48), (-5, 50), (0, 51), (5, 53), (8, 55),
     (10, 58), (12, 60), (18, 62), (20, 65), (25, 70), (30, 70), (40, 68),
     (50, 69), (60, 70), (70, 72), (80, 73), (90, 75), (100, 76),
     (110, 74), (120, 73), (130, 72), (140, 72), (150, 70), (160, 69),
     (170, 66), (178, 65), (170, 60), (162, 58), (158, 52), (150, 45),
     (142, 40), (140, 35), (135, 33), (130, 31), (127, 35), (122, 38),
     (120, 32), (115, 25), (110, 20), (108, 12), (105, 8), (100, 8),
     (98, 12), (95, 16), (92, 20), (88, 22), (85, 19), (80, 15), (77, 8),
     (75, 12), (72, 20), (68, 23), (65, 25), (60, 25), (57, 26), (54, 27),
     (52, 28), (50, 30), (48, 30), (46, 32), (44, 35), (42, 38), (40, 40),
     (38, 42), (35, 42), (33, 40), (30, 38), (28, 38), (26, 38), (23, 36),
     (20, 38), (18, 40), (15, 40), (12, 42), (10, 44), (8, 44), (5, 43),
     (3, 43), (0, 40), (-2, 37), (-6, 36), (-9, 37)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)],
    [(130, 31), (132, 33), (134, 34), (137, 35), (139, 37), (141, 39),
     (141, 42), (143, 44), (145, 44), (142, 42), (140, 38), (138, 35),
     (136, 33), (133, 32)],
    [(95, 5), (100, 0), (104, -3), (106, -6), (103, -5), (100, 0)],
    [(109, 1), (113, 4), (117, 6), (119, 1), (117, -3), (113, -4),
     (110, -2)],
    [(131, -1), (136, -2), (141, -3), (146, -6), (150, -9), (146, -8),
     (141, -8), (136, -4), (132, -2)],
    [(105, -6), (110, -7), (114, -7), (114, -8), (108, -8), (105, -7)],
    [(119, 0), (121, 1), (123, 0), (121, -2), (120, -4), (119, -2)],
    [(114, -22), (114, -30), (115, -33), (118, -35), (124, -33),
     (130, -32), (135, -35), (138, -35), (140, -38), (145, -38),
     (150, -37), (153, -32), (153, -27), (150, -22), (146, -19),
     (142, -15), (142, -11), (137, -12), (135, -15), (132, -12),
     (130, -13), (126, -14), (122, -17), (118, -20)],
    [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38),
     (175, -40), (172, -43), (168, -46)],
]


# ------------------------------------------------------- illustrations
# All three are drawn with code — original art, no photos.

def ill_hormuz(draw, x0, y0, w, h):
    """Oil tanker on fire in the Strait of Hormuz."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(18, 38, 66))
    # sea band
    draw.rectangle([x0, y0 + h - 16, x0 + w, y0 + h], fill=(28, 62, 96))
    for wx in (x0 + 12, x0 + 60, x0 + 120, x0 + 180, x0 + 240, x0 + 285):
        draw.arc([wx, y0 + h - 12, wx + 22, y0 + h - 2], 180, 360,
                 fill=(150, 190, 220), width=2)
    # smoke column above the tanker
    for cx, cy, r in ((150, 14, 11), (162, 11, 9), (138, 16, 9),
                      (172, 14, 8), (128, 20, 7)):
        draw.ellipse([x0 + cx - r, y0 + cy - r, x0 + cx + r, y0 + cy + r],
                     fill=(70, 70, 70))
    # explosion starburst: orange spikes around the blast point
    bx, by = x0 + 155, y0 + 26
    for dx, dy in ((-16, -6), (-12, -14), (-4, -18), (4, -16), (12, -12),
                   (18, -4), (16, 6), (8, 12), (-2, 12), (-12, 8)):
        draw.line([bx, by, bx + dx, by + dy], fill=(255, 140, 0), width=3)
    draw.ellipse([bx - 9, by - 9, bx + 9, by + 9], fill=(255, 200, 60))
    draw.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=(255, 240, 180))
    # tanker hull and deck
    draw.rectangle([x0 + 40, y0 + 34, x0 + 270, y0 + 44], fill=(120, 40, 30))
    draw.rectangle([x0 + 40, y0 + 44, x0 + 270, y0 + 48], fill=(60, 20, 16))
    # cargo tanks on deck
    for tx in (70, 110, 150, 190):
        draw.rectangle([x0 + tx, y0 + 26, x0 + tx + 30, y0 + 34],
                       fill=(200, 200, 200))
    # bridge superstructure + funnel
    draw.rectangle([x0 + 232, y0 + 18, x0 + 262, y0 + 34], fill=(240, 240, 240))
    draw.rectangle([x0 + 236, y0 + 22, x0 + 258, y0 + 26], fill=(30, 60, 100))
    draw.rectangle([x0 + 52, y0 + 22, x0 + 62, y0 + 34], fill=(200, 60, 30))
    draw.text((x0 + 6, y0 + 3), "STRAIT OF HORMUZ",
              font=SANS_B(10), fill=(255, 255, 255))


def ill_ras_tanura(draw, x0, y0, w, h):
    """Ras Tanura refinery at dusk, flare burning, smoke rising."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(38, 30, 24))
    # dusk sky band
    draw.rectangle([x0, y0, x0 + w, y0 + 14], fill=(90, 55, 35))
    # black smoke plume from the left column
    for cx, cy, r in ((95, 14, 12), (108, 12, 10), (84, 14, 9),
                      (118, 12, 8), (76, 18, 7)):
        draw.ellipse([x0 + cx - r, y0 + cy - r, x0 + cx + r, y0 + cy + r],
                     fill=(25, 25, 25))
    # distillation columns with banding
    for col_x, col_h, col_w in ((70, 34, 26), (120, 42, 22), (165, 30, 26)):
        draw.rectangle([x0 + col_x, y0 + h - 6 - col_h,
                        x0 + col_x + col_w, y0 + h - 6],
                       fill=(140, 150, 160))
        for by in range(y0 + h - 6 - col_h + 6, y0 + h - 6, 7):
            draw.line([x0 + col_x, by, x0 + col_x + col_w, by],
                      fill=(90, 100, 110), width=1)
    # horizontal pipe run between columns
    draw.line([x0 + 60, y0 + h - 12, x0 + 210, y0 + h - 12],
              fill=(110, 118, 128), width=3)
    # flare stack with flame
    draw.rectangle([x0 + 232, y0 + 8, x0 + 238, y0 + h - 6],
                   fill=(120, 125, 130))
    draw.polygon([(x0 + 235, y0 + 2), (x0 + 228, y0 + 12), (x0 + 242, y0 + 12)],
                 fill=(255, 180, 40))
    draw.polygon([(x0 + 235, y0 + 6), (x0 + 231, y0 + 13), (x0 + 239, y0 + 13)],
                 fill=(255, 230, 120))
    # ground line
    draw.line([x0, y0 + h - 6, x0 + w, y0 + h - 6], fill=(200, 170, 120),
              width=2)
    draw.text((x0 + 6, y0 + 3), "RAS TANURA",
              font=SANS_B(10), fill=(255, 255, 255))


def ill_shenzhou(draw, x0, y0, w, h):
    """Shenzhou-24 rocket climbing past Earth into a starry sky."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(10, 16, 38))
    # stars at fixed positions
    for sx, sy in ((20, 10), (55, 6), (90, 16), (250, 8), (285, 14),
                   (30, 30), (265, 28), (15, 44), (300, 40), (200, 10),
                   (230, 22), (120, 8), (150, 30)):
        draw.ellipse([x0 + sx, y0 + sy, x0 + sx + 2, y0 + sy + 2],
                     fill=(255, 255, 255))
    # Earth arc along the bottom, clipped to the box: a circle whose
    # top arc crosses the box, filled down to the box bottom edge.
    import math
    arc_cx = x0 + w // 2
    arc_cy = y0 + h + 186
    arc_r = 200
    arc_pts = []
    for ax in range(x0, x0 + w + 1, 6):
        ay = arc_cy - math.sqrt(arc_r ** 2 - (ax - arc_cx) ** 2)
        arc_pts.append((ax, min(ay, y0 + h)))
    draw.polygon(arc_pts + [(x0 + w, y0 + h), (x0, y0 + h)],
                 fill=(40, 90, 160))
    draw.line(arc_pts, fill=(120, 180, 230), width=2)
    # small green landmasses sitting on the arc, inside the box
    draw.ellipse([x0 + 60, y0 + h - 12, x0 + 80, y0 + h - 2],
                 fill=(60, 130, 90))
    draw.ellipse([x0 + 210, y0 + h - 11, x0 + 226, y0 + h - 2],
                 fill=(60, 130, 90))
    # rocket body, nose cone, fins, flame
    rx = x0 + 150
    draw.polygon([(rx - 9, y0 + 8), (rx + 9, y0 + 8), (rx, y0 + 1)],
                 fill=(200, 40, 40))
    draw.rectangle([rx - 9, y0 + 8, rx + 9, y0 + 34], fill=(240, 240, 240))
    draw.rectangle([rx - 9, y0 + 20, rx + 9, y0 + 24], fill=(200, 40, 40))
    draw.polygon([(rx - 9, y0 + 28), (rx - 16, y0 + 38), (rx - 9, y0 + 38)],
                 fill=(180, 30, 30))
    draw.polygon([(rx + 9, y0 + 28), (rx + 16, y0 + 38), (rx + 9, y0 + 38)],
                 fill=(180, 30, 30))
    draw.polygon([(rx, y0 + 38), (rx - 5, y0 + 48), (rx + 5, y0 + 48)],
                 fill=(255, 180, 40))
    draw.polygon([(rx, y0 + 40), (rx - 3, y0 + 46), (rx + 3, y0 + 46)],
                 fill=(255, 230, 120))
    draw.text((x0 + 6, y0 + 3), "JIUQUAN",
              font=SANS_B(10), fill=(255, 255, 255))


ILLUSTRATIONS = [ill_hormuz, ill_ras_tanura, ill_shenzhou]


# ------------------------------------------------------------ sections

def draw_masthead(draw):
    centred(draw, W // 2, 10, "THE WORLD TODAY", SERIF_B(54), INK)
    draw.line([(M, 76), (W - M, 76)], fill=INK, width=2)
    draw.text((M, 82), "WEDNESDAY, 25 NOVEMBER 2026",
              font=SANS_B(13), fill=INK)
    right = "40 STORIES  ·  9 REGIONS  ·  ONE DAY"
    draw.text((W - M - SANS_B(13).getlength(right), 82), right,
              font=SANS_B(13), fill=INK)
    # red date band
    draw.rectangle([M, 100, W - M, 128], fill=RED)
    centred(draw, W // 2, 107,
            "THE DAY IN WORLD NEWS  —  WEDNESDAY 25 NOVEMBER 2026",
            SANS_B(15), (255, 255, 255))
    # region counts, counted from the data
    counts = {}
    for _, region, _ in GRID:
        counts[region] = counts.get(region, 0) + 1
    counts["MIDDLE EAST"] += 2  # headlines 1 and 2
    counts["TECH & SPACE"] += 1  # headline 3
    parts = ["%s %d" % (r, counts[r]) for r in REGION_ORDER if counts.get(r)]
    centred(draw, W // 2, 136, "   ·   ".join(parts), SANS_B(12), INK)


def draw_numbers(draw):
    draw.text((M, 160), "THE DAY IN NUMBERS", font=SANS_B(14), fill=RED)
    box_w = (976 - 5 * 8) // 6
    y0, y1 = 182, 232
    for i, (big, label) in enumerate(NUMBERS):
        bx = M + i * (box_w + 8)
        draw.rectangle([bx, y0, bx + box_w, y1], outline=INK, width=1)
        draw.text((bx + 8, y0 + 4), big, font=SANS_B(18), fill=INK)
        draw_wrapped(draw, bx + 8, y0 + 27, label, SANS(9), box_w - 14,
                     GREY, 10)


def draw_top_stories(draw):
    draw.text((M, 242), "TOP STORIES", font=SANS_B(14), fill=RED)
    card_w = (976 - 24) // 3
    card_y, card_h = 260, 160
    for i, (num, title, summary, _label) in enumerate(TOP_STORIES):
        cx = M + i * (card_w + 12)
        draw.rectangle([cx, card_y, cx + card_w, card_y + card_h],
                       outline=INK, width=1)
        ILLUSTRATIONS[i](draw, cx + 1, card_y + 1, card_w - 2, 56)
        draw.text((cx + 8, card_y + 62), num, font=SERIF_B(20), fill=RED)
        title_lines = wrap(title, SERIF_B(17), card_w - 38)
        ty = card_y + 62
        for line in title_lines:
            draw.text((cx + 30, ty), line, font=SERIF_B(17), fill=INK)
            ty += 20
        draw_wrapped(draw, cx + 8, ty + 4, summary, SANS(11), card_w - 16,
                     BODY, 14)
    return card_y + card_h


def draw_map(draw, y0):
    """World map, height 140, equirectangular, with 11 numbered pins."""
    draw.text((M, y0), "WHERE IT HAPPENED", font=SANS_B(14), fill=RED)
    map_y0, map_y1 = y0 + 18, y0 + 158
    draw.rectangle([M, map_y0, W - M, map_y1], fill=SEA, outline=INK, width=1)

    def px(lon):
        return M + (lon + 180) / 360.0 * 976

    def py(lat):
        return map_y0 + (85 - lat) / 145.0 * 140

    # graticule every 30 degrees
    for lon in range(-180, 181, 30):
        x = px(lon)
        draw.line([(x, map_y0), (x, map_y1)], fill=(190, 205, 220), width=1)
    for lat in range(-60, 86, 30):
        y = py(lat)
        draw.line([(M, y), (W - M, y)], fill=(190, 205, 220), width=1)
    # continents
    for poly in CONTINENTS:
        pts = [(px(lon), py(lat)) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=(120, 110, 90))
    # pins
    for i, (lat, lon, _label) in enumerate(PINS, start=1):
        x, y = px(lon), py(lat)
        draw.ellipse([x - 9, y - 9, x + 9, y + 9], fill=RED,
                     outline=(255, 255, 255), width=1)
        num = str(i)
        nf = SANS_B(10 if len(num) == 1 else 9)
        draw.text((x - nf.getlength(num) / 2, y - 6), num, font=nf,
                  fill=(255, 255, 255))
    # pin key, two lines
    key1 = "  ·  ".join("%d. %s" % (i + 1, PINS[i][2]) for i in range(6))
    key2 = "  ·  ".join("%d. %s" % (i + 1, PINS[i][2]) for i in range(6, 11))
    draw.text((M, map_y1 + 4), key1, font=SANS(9), fill=GREY)
    draw.text((M, map_y1 + 15), key2, font=SANS(9), fill=GREY)
    return map_y1 + 26


def draw_also(draw, y0):
    """Stories 4-40, region-ordered, split in half across two columns."""
    draw.text((M, y0), "ALSO ON WEDNESDAY 25 NOVEMBER",
              font=SANS_B(14), fill=RED)
    col_w = (976 - 20) // 2
    half = (len(GRID) + 1) // 2
    columns = [GRID[:half], GRID[half:]]
    bottom = y0
    for ci, stories in enumerate(columns):
        cx = M + ci * (col_w + 20)
        y = y0 + 18
        last_region = None
        for num, region, title in stories:
            if region != last_region:
                draw.text((cx, y), region, font=SANS_B(10), fill=RED)
                y += 20
                last_region = region
            text = "%d. %s" % (num, title)
            y = draw_wrapped(draw, cx + 12, y, text, SANS(10),
                             col_w - 12, INK, 10)
        bottom = max(bottom, y)
    return bottom


def draw_date_check(draw, y0):
    draw.rectangle([M, y0, W - M, y0 + 54], outline=RED, width=2)
    draw.text((M + 8, y0 + 5), "DATE CHECK — LEFT OUT ON PURPOSE",
              font=SANS_B(11), fill=RED)
    draw_wrapped(draw, M + 8, y0 + 19, DATE_CHECK_BODY, SANS(10),
                 976 - 16, INK, 12)
    return y0 + 54


def draw_footer(draw, y0):
    draw.line([(M, y0), (W - M, y0)], fill=INK, width=1)
    return draw_wrapped(draw, M, y0 + 4, SOURCES, SANS(8), 976, GREY, 11)


def render():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw)
    draw_numbers(draw)
    cards_bottom = draw_top_stories(draw)
    map_bottom = draw_map(draw, cards_bottom + 8)
    also_bottom = draw_also(draw, map_bottom + 8)
    dc_bottom = draw_date_check(draw, also_bottom + 8)
    end = draw_footer(draw, dc_bottom + 6)
    assert end <= H, "page overflow: footer ends at y=%d" % end
    return img


def main():
    out = os.environ.get("RENDER_OUT") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = render()
    img.save(out, "PNG")
    print("wrote %s (%dx%d)" % (out, W, H))


if __name__ == "__main__":
    main()
