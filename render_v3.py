#!/usr/bin/env python3
"""news-image-20261120 v3 renderer (akun kedua @huaminyo).

Draws a one-page broadsheet summing up Friday 20 November 2026:
36 stories, 7 regions, 13 illustrated. Fresh implementation written for v3:
cream broadsheet, big serif masthead, numbers strip, region bar, 3 lead
stories, 10 feature cards, dot-grid world map with numbered pins, 23 briefs
and a DATE CHECK footer. Deterministic: no network, no randomness, no clock.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 241, 222)
INK = (20, 20, 20)
RED = (158, 27, 27)
DARKRED = (122, 18, 18)
NAVY = (16, 35, 63)
TEAL = (15, 94, 92)
GRAY = (85, 85, 85)
LIGHTGRAY = (170, 165, 145)
CARD = (255, 253, 244)
GOLD = (176, 124, 12)

FD = "/usr/share/fonts/truetype/dejavu"
FN = "/usr/share/fonts/truetype/noto"


def F(name, size):
    """Load a font, falling back through known paths then PIL default."""
    paths = [
        os.path.join(FN, "NotoSerifDisplay-Black.ttf"),
        os.path.join(FN, "NotoSerifDisplay-Bold.ttf"),
        os.path.join(FD, "DejaVuSerif-Bold.ttf"),
        os.path.join(FD, "DejaVuSerif.ttf"),
        os.path.join(FD, "DejaVuSans-Bold.ttf"),
        os.path.join(FD, "DejaVuSans.ttf"),
    ]
    want = {
        "mast": "NotoSerifDisplay-Black.ttf",
        "serif_b": "DejaVuSerif-Bold.ttf",
        "serif": "DejaVuSerif.ttf",
        "serif_i": "DejaVuSerif-Italic.ttf",
        "sans_b": "DejaVuSans-Bold.ttf",
        "sans": "DejaVuSans.ttf",
    }.get(name, "DejaVuSans.ttf")
    for base in (FN, FD):
        p = os.path.join(base, want)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def wrap(d, text, font, max_w):
    """Greedy word wrap to a pixel width; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(d, x, y, text, font, max_w, max_lines, fill=INK, leading=None):
    """Draw wrapped text; returns y after the last line drawn."""
    if leading is None:
        leading = font.size + 3
    for i, line in enumerate(wrap(d, text, font, max_w)[:max_lines]):
        d.text((x, y + i * leading), line, font=font, fill=fill)
    n = min(len(wrap(d, text, font, max_w)), max_lines)
    return y + n * leading


# ---------------------------------------------------------------- stories
# (n, place, beat, tag, headline, body) -- tag in (REPORTED, CLAIM, FORECAST,
#  ONGOING, EARLY TRIAL, ESTIMATE, OFFICIALS SAY)
LEAD = [
    (1, "KYIV, UKRAINE", "WAR", "REPORTED",
     "Russia fires 100+ missiles at Ukraine; three Kyiv bridges hit",
     "Overnight barrage of ~100 missiles and 400+ drones kills 6 in Kyiv and "
     "wounds 15; three Dnipro bridges damaged, power cut across 10 regions. "
     "(Kyiv City Military Administration; Reuters)"),
    (2, "ODISHA, INDIA", "CYCLONE", "REPORTED",
     "Cyclone Akvan makes landfall near Gopalpur",
     "Severe storm crosses the Odisha coast; 300,000+ evacuated, winds 90-100 "
     "km/h gusting 110, 209mm of rain at Patrapur. (IMD; PTI)"),
    (3, "ANTALYA, TURKIYE", "CLIMATE", "REPORTED",
     "COP31 reaches its final day deadlocked",
     "Closing draft drops fossil-fuel wording and the $120bn adaptation gap "
     "stays unresolved; hosts push a '35 by 35' clean-power goal. "
     "(UN News; Reuters)"),
]

FEATURE = [
    (4, "ASIA", "MARKETS", "REPORTED",
     "AI sell-off sinks Asia to worst week since 2020",
     "Taiex -6.2%, Kospi -5.2%, Nikkei -5.1% as chipmakers lead the slide. "
     "(Reuters)"),
    (5, "SPACE", "SCIENCE", "REPORTED",
     "BepiColombo closes in on Mercury",
     "After 8 years and 6bn miles, the ESA-JAXA probe's orbit burn is "
     "Saturday. (ESA)"),
    (6, "BRUSSELS", "POLITICS", "REPORTED",
     "UK and EU seal 'reset' deal",
     "Youth mobility, food trade and carbon markets agreed a decade after "
     "Brexit. (Al Jazeera)"),
    (7, "TOKYO", "ECONOMY", "REPORTED",
     "Japan inflation holds at 2.2%",
     "Oct core CPI tops the 2% target for a second month; BoJ hike eyed. "
     "(Reuters)"),
    (8, "BEIJING", "ECONOMY", "REPORTED",
     "China holds lending rates",
     "1-year 3.00%, 5-year 3.50% for an 18th month, as expected. (PBOC)"),
    (9, "WELLINGTON", "SPORT", "REPORTED",
     "Phillips makes history with 118",
     "First NZ batter with centuries in all formats vs India. (ICC)"),
    (10, "HEALTH", "SCIENCE", "EARLY TRIAL",
     "Cancer pill shrinks tumours 60.7%",
     "Daraxonrasib + chemo beats chemo alone in an early trial. (Reuters)"),
    (11, "SENEGAL", "MIGRATION", "REPORTED",
     "Migrant boat capsizes; 4 dead",
     "Dozens missing, 50-100 aboard, on the Canaries route. (Al Jazeera)"),
    (12, "ROME", "LABOUR", "ONGOING",
     "Italy's CGIL holds 24-hour general strike",
     "Rallies in ~100 squares against the 2027 budget. (CGIL; AFP)"),
    (13, "SALVADOR", "POLITICS", "REPORTED",
     "Bukele files for third term",
     "Feb 2027 vote; rights groups object to the bid. (AP)"),
]

BRIEFS = [
    (14, "BRAZIL", "Lula meets chief Raoni on land rights. (Al Jazeera)"),
    (15, "SEOUL", "Ruling party moves to impeach top judge. (SBS)"),
    (16, "BOUGAINVILLE", "Rio Tinto pledges $370m for Panguna. (ABC)"),
    (17, "CANBERRA", "CBO warns AUKUS subs could sink US fleet. (ABC)"),
    (18, "FLORIDA", "St. Johns River hits record 18.3 ft. (AP)"),
    (19, "IOWA", "Army detonates 68 unstable explosive barrels. (AP)"),
    (20, "TONGA", "Emergency declared as El Nino drought bites. (RNZ)"),
    (21, "WASHINGTON", "Pentagon: US war cost vs Iran $48.3bn. (AP)"),
    (22, "LONDON", "UK & Norway fund \u00a3100m+ for Ukraine ships. (BBC)"),
    (23, "COPENHAGEN", "Denmark OKs Greenland defence bill. (AFP)"),
    (24, "JAKARTA", "Parliament passes asset-forfeiture bill. (Reuters)"),
    (25, "HORMUZ", "46 ships waiting; Brent $92.50. (UKMTO)"),
    (26, "NEW DELHI", "Pakistan minister in India, first since war. (PTI)"),
    (27, "SOUTH AFRICA", "Murders down to 5,590 in Jul-Sep. (SAPS)"),
    (28, "QATAR", "U17 World Cup: Austria stun Argentina 2-0. (FIFA)"),
    (29, "IRAQ", "Kataib Hezbollah deadline to quit Jurf al-Sakhar. (AP)"),
    (30, "TURIN", "Alcaraz, Medvedev into ATP Finals semis. (ATP)"),
    (31, "LOS ANGELES", "Thomas Markle ruled fit to stand trial. (BBC)"),
    (32, "LAS VEGAS", "Russell fastest in wet F1 practice. (F1)"),
    (33, "SEOUL", "111 caught cheating in Suneung exam. (Yonhap)"),
    (34, "CALIFORNIA", "Nvidia probed over China chip sales. (Reuters)"),
    (35, "BERLIN", "Young Germans rally against conscription. (dpa)"),
    (36, "GOLD", "Falls 2.6% to ~$3,526, lowest since Sept. (ABC)"),
]

NUMBERS = [
    ("300,000+", "evacuated ahead of Cyclone Akvan"),
    ("100+", "missiles fired at Ukraine overnight"),
    ("-5.1%", "Nikkei's Friday fall; worst week since 2020"),
    ("2.2%", "Japan Oct core CPI; BoJ rate hike eyed"),
    ("118", "Phillips' historic century vs India"),
    ("$120bn", "COP31 adaptation gap left unresolved"),
]

# (label, count, colour) -- sums to 36
REGIONS = [
    ("EUROPE 8", 8, (31, 78, 121)),
    ("ASIA-PACIFIC 8", 8, (15, 94, 92)),
    ("AMERICAS 8", 8, (140, 47, 57)),
    ("OCEANIA 4", 4, (106, 127, 42)),
    ("MIDEAST 3", 3, (176, 124, 12)),
    ("WORLD 3", 3, (91, 91, 138)),
    ("AFRICA 2", 2, (196, 106, 27)),
]

DATE_CHECK = (
    "Left out as Thursday 19 November news: the Trump-Xi-Putin summit in "
    "Shenzhen \u00b7 the ICJ Rohingya genocide ruling \u00b7 Anthropic's $83 IPO "
    "pricing and Nasdaq debut \u00b7 GTA VI's midnight launch \u00b7 the Kerch "
    "Bridge strike \u00b7 the Senate's 51-48 Iran war-powers vote \u00b7 "
    "Voyager 1 one light-day out."
)

FOOTER = (
    "Every story above happened, or was first reported, on Friday 20 November 2026 "
    "in at least one time zone. Unverified claims are attributed, not stated as fact. "
    "Sources: Reuters, AP, AFP, BBC, IMD, UN News, Al Jazeera, ICC, PBOC, ESA, UKMTO. "
    "All illustrations are original vector drawings."
)


# ------------------------------------------------------------ illustrations
def chip(d, x, y, w, text, bg, fg=(255, 255, 255), size=10):
    """Small caption band pinned to the bottom of an illustration."""
    f = F("sans_b", size)
    while d.textlength(text, font=f) > w - 10 and len(text) > 4:
        text = text[:-1]
    if d.textlength(text, font=f) > w - 10:
        text = text.rstrip(" .·") + "…"
    d.rectangle([x, y, x + w, y + size + 8], fill=bg)
    d.text((x + 5, y + 4), text, font=f, fill=fg)


def stars(d, x, y, w, h, n=26):
    """Deterministic star field (positions from a fixed hash walk)."""
    v = 12345
    for _ in range(n):
        v = (v * 1103515245 + 12345) & 0x7FFFFFFF
        sx = x + (v % max(w - 4, 1)) + 2
        v = (v * 1103515245 + 12345) & 0x7FFFFFFF
        sy = y + (v % max(h - 4, 1)) + 2
        r = 1 if (v % 3) else 2
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 244, 200))


def art_kyiv(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(13, 22, 43))
    stars(d, x, y, w, h - 30, 30)
    d.ellipse([x + w - 34, y + 8, x + w - 12, y + 30], fill=(240, 230, 190))
    # missile trails
    for i, (sx, sy, ex, ey) in enumerate([
            (0.08, 0.95, 0.30, 0.18), (0.30, 0.95, 0.52, 0.10),
            (0.55, 0.95, 0.78, 0.22), (0.72, 0.95, 0.92, 0.35)]):
        px0, py0 = x + sx * w, y + sy * h
        px1, py1 = x + ex * w, y + ey * h
        mx, my = (px0 + px1) / 2, min(py0, py1) - 26
        pts = []
        for t in range(21):
            t /= 20
            pts.append(((1 - t) ** 2 * px0 + 2 * (1 - t) * t * mx + t * t * px1,
                        (1 - t) ** 2 * py0 + 2 * (1 - t) * t * my + t * t * py1))
        d.line(pts, fill=(255, 170, 60), width=2)
        d.ellipse([px1 - 4, py1 - 4, px1 + 4, py1 + 4], fill=(255, 220, 120))
    # skyline
    base = y + h - 26
    bx = x + 4
    heights = [0.42, 0.55, 0.34, 0.62, 0.48, 0.70, 0.38, 0.58, 0.45, 0.66, 0.40]
    bw = (w - 8) / len(heights)
    for i, hh in enumerate(heights):
        bh = hh * (h - 40)
        d.rectangle([bx, base - bh, bx + bw - 2, base], fill=(8, 12, 26))
        for wy in range(3):
            for wx in range(2):
                if (i * 3 + wy * 2 + wx) % 3 == 0:
                    d.rectangle([bx + 3 + wx * 6, base - bh + 5 + wy * 9,
                                 bx + 6 + wx * 6, base - bh + 8 + wy * 9],
                                fill=(255, 200, 90))
        bx += bw
    # river + bridges
    d.rectangle([x, base, x + w, y + h - 14], fill=(24, 60, 110))
    for bx0 in (0.10, 0.45, 0.75):
        cx = x + bx0 * w
        d.arc([cx - 26, base - 6, cx + 26, base + 22], 180, 360,
              fill=(200, 210, 220), width=3)
        d.line([cx - 26, base + 8, cx + 26, base + 8], fill=(200, 210, 220),
               width=2)
    # explosions on two bridges
    for ex in (0.10, 0.75):
        cx, cy = x + ex * w, base + 2
        for r, col in ((10, (255, 120, 20)), (6, (255, 200, 80)),
                       (3, (255, 240, 180))):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    chip(d, x, y + h - 16, w, "KYIV \u00b7 OVERNIGHT BARRAGE \u00b7 100+ MISSILES",
         (10, 16, 32))


def art_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 90, 130))
    # land (India east coast) on the left
    d.polygon([(x, y), (x + w * 0.34, y), (x + w * 0.26, y + h * 0.45),
               (x + w * 0.38, y + h * 0.75), (x + w * 0.30, y + h),
               (x, y + h)], fill=(214, 196, 150))
    d.text((x + 6, y + 6), "ODISHA", font=F("sans_b", 10), fill=(90, 60, 20))
    d.text((x + 6, y + 18), "INDIA", font=F("sans_b", 9), fill=(90, 60, 20))
    # spiral
    cx, cy = x + w * 0.62, y + h * 0.46
    for r in range(34, 4, -6):
        d.arc([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8],
              200 - r * 6, 200 - r * 6 + 250, fill=(255, 255, 255), width=3)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 255, 255))
    # rain slashes
    for i in range(12):
        rx = x + w * 0.42 + i * (w * 0.045)
        ry = y + 6 + (i % 3) * 12
        d.line([rx, ry, rx - 5, ry + 10], fill=(180, 220, 240), width=2)
    # Gopalpur dot + label box below it
    gx, gy = x + w * 0.335, y + h * 0.52
    d.ellipse([gx - 4, gy - 4, gx + 4, gy + 4], fill=RED)
    d.ellipse([gx - 7, gy - 7, gx + 7, gy + 7], outline=RED, width=2)
    f_lab = F("sans_b", 8)
    lab = "GOPALPUR"
    lw = d.textlength(lab, font=f_lab) + 8
    d.rectangle([gx - 4, gy + 10, gx - 4 + lw, gy + 22], fill=(8, 50, 80))
    d.text((gx, gy + 12), lab, font=f_lab, fill=(255, 255, 255))
    f_bay = F("sans_b", 8)
    bay = "BAY OF BENGAL"
    d.text((x + w - 4 - d.textlength(bay, font=f_bay), y + 6), bay,
           font=f_bay, fill=(200, 230, 245))
    chip(d, x, y + h - 16, w, "LANDFALL 08:00 \u00b7 GUSTS 110 KM/H",
         (8, 50, 80))


def art_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(230, 240, 235))
    # globe
    cx, cy, r = x + w * 0.30, y + h * 0.44, min(w, h) * 0.34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(70, 140, 190),
              outline=(20, 80, 120), width=2)
    for ox, oy, orad in ((-0.4, -0.3, 0.30), (0.35, 0.1, 0.34),
                         (-0.1, 0.45, 0.26), (0.45, -0.4, 0.2)):
        d.ellipse([cx + ox * r - orad * r, cy + oy * r - orad * r,
                   cx + ox * r + orad * r, cy + oy * r + orad * r],
                  fill=(90, 170, 110))
    # thermometer
    tx = x + w * 0.60
    d.rectangle([tx, y + h * 0.14, tx + 10, y + h * 0.72], fill=(255, 255, 255),
                outline=(120, 120, 120))
    d.rectangle([tx + 2, y + h * 0.30, tx + 8, y + h * 0.72], fill=(220, 40, 40))
    d.ellipse([tx - 4, y + h * 0.68, tx + 14, y + h * 0.86], fill=(220, 40, 40))
    d.text((tx + 16, y + h * 0.30), "1.5\u00b0C", font=F("sans_b", 12),
           fill=DARKRED)
    d.text((tx + 16, y + h * 0.30 + 15), "OVERSHOOT", font=F("sans_b", 8),
           fill=DARKRED)
    # stamp
    sx, sy = x + w * 0.62, y + h * 0.10
    d.rectangle([sx, sy, sx + 92, sy + 24], outline=RED, width=3)
    d.text((sx + 6, sy + 5), "NO DEAL YET", font=F("sans_b", 11), fill=RED)
    chip(d, x, y + h - 16, w, "ANTALYA \u00b7 35 BY 35 PUSHED \u00b7 21 ISSUES OPEN",
         (20, 90, 70))


def art_markets(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(12, 12, 14))
    # grid
    for i in range(1, 4):
        gy = y + h * i / 4
        d.line([x + 4, gy, x + w - 4, gy], fill=(50, 50, 55), width=1)
    # falling line
    pts = []
    vals = [0.16, 0.24, 0.22, 0.38, 0.34, 0.52, 0.48, 0.66, 0.78]
    for i, v in enumerate(vals):
        pts.append((x + 8 + i * (w - 16) / (len(vals) - 1), y + 8 + v * (h - 34)))
    d.line(pts, fill=(255, 60, 60), width=3)
    d.polygon(pts + [(pts[-1][0], y + h - 18), (pts[0][0], y + h - 18)],
              fill=(120, 20, 20))
    f = F("sans_b", 11)
    d.text((x + 6, y + 4), "NIKKEI -5.1%", font=f, fill=(255, 120, 120))
    d.text((x + w - 78, y + 4), "TAIEX -6.2%", font=f, fill=(255, 120, 120))
    d.text((x + 6, y + h - 30), "KOSPI -5.2%", font=f, fill=(255, 120, 120))
    chip(d, x, y + h - 16, w, "WORST WEEK SINCE 2020", (120, 20, 20))


def art_space(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(8, 10, 26))
    stars(d, x, y, w, h - 16, 22)
    # Mercury
    cx, cy, r = x + w * 0.74, y + h * 0.40, min(w, h) * 0.30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(170, 160, 145))
    for ox, oy, orad in ((-0.3, -0.2, 0.22), (0.25, 0.15, 0.28),
                         (0.1, -0.45, 0.16), (-0.35, 0.35, 0.18)):
        d.ellipse([cx + ox * r - orad * r, cy + oy * r - orad * r,
                   cx + ox * r + orad * r, cy + oy * r + orad * r],
                  fill=(130, 120, 105))
    # trajectory + probe
    d.arc([x + 6, y + h * 0.30, x + w * 0.85, y + h * 1.05], 200, 330,
          fill=(120, 200, 255), width=2)
    px, py = x + w * 0.34, y + h * 0.52
    d.rectangle([px - 5, py - 3, px + 5, py + 3], fill=(220, 220, 220))
    d.rectangle([px - 14, py - 1, px - 5, py + 1], fill=(80, 140, 220))
    d.rectangle([px + 5, py - 1, px + 14, py + 1], fill=(80, 140, 220))
    d.text((x + 6, y + 4), "BEPICOLOMBO", font=F("sans_b", 10),
           fill=(180, 220, 255))
    chip(d, x, y + h - 16, w, "8 YEARS \u00b7 6BN MILES", (20, 30, 70))


def art_reset(d, x, y, w, h):
    # EU flag left, Union Jack right, document centre
    d.rectangle([x, y, x + w // 2, y + h - 16], fill=(0, 51, 153))
    cx, cy = x + w // 4, y + (h - 16) // 2
    import math
    for k in range(12):
        a = math.pi * 2 * k / 12 - math.pi / 2
        sx, sy = cx + 26 * math.cos(a), cy + 20 * math.sin(a)
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 204, 0))
    # union jack (simplified, line-based)
    jx = x + w // 2
    jh = h - 16
    d.rectangle([jx, y, x + w, y + jh], fill=(1, 33, 105))
    d.line([jx, y, x + w, y + jh], fill=(255, 255, 255), width=11)
    d.line([x + w, y, jx, y + jh], fill=(255, 255, 255), width=11)
    d.line([jx, y, x + w, y + jh], fill=(200, 16, 46), width=4)
    d.line([x + w, y, jx, y + jh], fill=(200, 16, 46), width=4)
    cxj = jx + (w - w // 2) // 2
    cyj = y + jh // 2
    d.rectangle([cxj - 9, y, cxj + 9, y + jh], fill=(255, 255, 255))
    d.rectangle([jx, cyj - 9, x + w, cyj + 9], fill=(255, 255, 255))
    d.rectangle([cxj - 4, y, cxj + 4, y + jh], fill=(200, 16, 46))
    d.rectangle([jx, cyj - 4, x + w, cyj + 4], fill=(200, 16, 46))
    # document + seal
    dx, dy = x + w // 2 - 26, y + (h - 16) // 2 - 16
    d.rectangle([dx, dy, dx + 52, dy + 32], fill=(255, 255, 255),
                outline=(60, 60, 60))
    for i in range(3):
        d.line([dx + 6, dy + 7 + i * 7, dx + 34, dy + 7 + i * 7],
               fill=(120, 120, 120), width=2)
    d.ellipse([dx + 36, dy + 18, dx + 48, dy + 30], fill=RED)
    chip(d, x, y + h - 16, w, "SEALED AFTER A DECADE", (20, 60, 120))


def art_cpi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 238, 228))
    base = y + h - 26
    bars = [("SEP", 2.1, (150, 150, 150)), ("OCT", 2.2, TEAL),
            ("FCST", 2.3, (90, 90, 160))]
    bw = (w - 40) / 3
    for i, (lab, v, col) in enumerate(bars):
        bh = (v / 2.6) * (h - 44)
        bx = x + 14 + i * bw
        d.rectangle([bx, base - bh, bx + bw - 8, base], fill=col)
        d.text((bx, base - bh - 13), "%.1f%%" % v, font=F("sans_b", 10),
               fill=INK)
        d.text((bx, base + 2), lab, font=F("sans_b", 8), fill=GRAY)
    # 2% target line (dashed red; the chip below names the target)
    ty = base - (2.0 / 2.6) * (h - 44)
    for lx in range(x + 8, x + w - 8, 8):
        d.line([lx, ty, lx + 4, ty], fill=RED, width=2)
    chip(d, x, y + h - 16, w, "ABOVE TARGET 2ND MONTH", (60, 60, 60))


def art_rates(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(150, 20, 25))
    # bank building
    bx, by = x + 10, y + h - 44
    d.rectangle([bx, by, bx + 56, by + 28], fill=(255, 255, 255))
    d.polygon([(bx - 4, by), (bx + 28, by - 14), (bx + 60, by)],
              fill=(255, 255, 255))
    for i in range(4):
        d.rectangle([bx + 7 + i * 13, by + 6, bx + 12 + i * 13, by + 24],
                    fill=(150, 20, 25))
    # rate cards
    for i, (lab, v) in enumerate([("1-YEAR", "3.00%"), ("5-YEAR", "3.50%")]):
        cx = x + w - 118 + i * 58
        cy = y + 8
        d.rectangle([cx, cy, cx + 54, cy + 34], fill=(255, 255, 255))
        d.text((cx + 5, cy + 3), lab, font=F("sans_b", 8), fill=GRAY)
        d.text((cx + 5, cy + 15), v, font=F("sans_b", 13), fill=DARKRED)
    chip(d, x, y + h - 16, w, "HELD 18 MONTHS", (90, 10, 15))


def art_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(34, 120, 60))
    # pitch
    d.polygon([(x + w * 0.30, y), (x + w * 0.48, y),
               (x + w * 0.62, y + h - 16), (x + w * 0.22, y + h - 16)],
              fill=(220, 200, 160))
    # stumps
    sx = x + w * 0.38
    for i in range(3):
        d.line([sx + i * 5, y + 12, sx + i * 5, y + 26], fill=(255, 230, 150),
               width=2)
    # bat
    d.polygon([(x + w * 0.62, y + h * 0.30), (x + w * 0.70, y + h * 0.22),
               (x + w * 0.78, y + h * 0.42), (x + w * 0.70, y + h * 0.48)],
              fill=(230, 210, 170))
    d.line([x + w * 0.70, y + h * 0.22, x + w * 0.74, y + h * 0.12],
           fill=(120, 80, 40), width=3)
    # ball
    d.ellipse([x + w * 0.16, y + h * 0.30, x + w * 0.16 + 12,
               y + h * 0.30 + 12], fill=(200, 30, 30))
    d.text((x + 8, y + h - 44), "118", font=F("sans_b", 26),
           fill=(255, 255, 255))
    chip(d, x, y + h - 16, w, "NZ 368 \u00b7 ALL FORMATS", (10, 70, 35))


def art_pill(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(235, 240, 248))
    # capsule, tilted
    cx, cy = x + w * 0.34, y + h * 0.42
    d.ellipse([cx - 34, cy - 13, cx + 34, cy + 13], fill=(220, 60, 60))
    d.pieslice([cx - 34, cy - 13, cx + 34, cy + 13], 90, 270,
               fill=(255, 255, 255))
    d.ellipse([cx - 34, cy - 13, cx + 34, cy + 13], outline=(150, 40, 40),
              width=2)
    # magnifier over tumour dots
    mx, my = x + w * 0.72, y + h * 0.40
    d.ellipse([mx - 20, my - 20, mx + 20, my + 20], outline=(40, 80, 140),
              width=4)
    d.line([mx + 14, my + 14, mx + 26, my + 26], fill=(40, 80, 140), width=5)
    for ox, oy in ((-8, -6), (4, 2), (-2, 8)):
        d.ellipse([mx + ox - 3, my + oy - 3, mx + ox + 3, my + oy + 3],
                  fill=(200, 80, 80))
    d.text((x + 6, y + 4), "-60.7%", font=F("sans_b", 13), fill=RED)
    chip(d, x, y + h - 16, w, "1 IN 12 CLEAR \u00b7 EARLY TRIAL", (40, 80, 140))


def art_boat(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(20, 40, 80))
    d.ellipse([x + w - 30, y + 6, x + w - 12, y + 24], fill=(240, 230, 190))
    # waves
    for i in range(5):
        wy = y + h - 34 + i * 6
        for wx in range(0, w, 24):
            d.arc([x + wx, wy, x + wx + 24, wy + 10], 180, 360,
                  fill=(90, 150, 210), width=2)
    # boat hull + figures
    bx, by = x + w * 0.30, y + h * 0.52
    d.polygon([(bx, by), (bx + 70, by), (bx + 58, by + 14), (bx + 12, by + 14)],
              fill=(120, 70, 30))
    for i in range(4):
        fx = bx + 12 + i * 15
        d.ellipse([fx, by - 12, fx + 7, by - 5], fill=(255, 210, 170))
        d.rectangle([fx - 1, by - 5, fx + 8, by + 1], fill=(200, 60, 60))
    d.text((x + 6, y + 4), "YENNE COAST", font=F("sans_b", 9),
           fill=(200, 220, 240))
    chip(d, x, y + h - 16, w, "4 DEAD \u00b7 DOZENS MISSING", (10, 25, 55))


def art_strike(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(245, 240, 225))
    # banner
    d.rectangle([x + 8, y + 6, x + w - 8, y + 24], fill=(180, 30, 30))
    d.text((x + w // 2 - 30, y + 9), "SCIOPERO", font=F("sans_b", 11),
           fill=(255, 255, 255))
    # crowd silhouettes
    for i in range(7):
        hx = x + 10 + i * (w - 20) // 7
        hy = y + h - 40 + (i % 2) * 8
        d.ellipse([hx, hy, hx + 12, hy + 12], fill=(40, 40, 40))
        d.pieslice([hx - 4, hy + 10, hx + 16, hy + 34], 180, 360,
                   fill=(40, 40, 40))
    # placards
    for i, px in enumerate((0.20, 0.55, 0.80)):
        px0 = x + px * w
        d.line([px0, y + 30, px0, y + 52], fill=(90, 90, 90), width=2)
        d.rectangle([px0 - 9, y + 26, px0 + 9, y + 38], fill=(255, 255, 255),
                    outline=(40, 40, 40))
    chip(d, x, y + h - 16, w, "100 SQUARES \u00b7 24 HOURS", (120, 20, 20))


def art_ballot(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 70, 140))
    # ballot box
    bx, by = x + w * 0.30, y + h * 0.34
    d.rectangle([bx, by, bx + 74, by + 44], fill=(255, 255, 255))
    d.rectangle([bx - 4, by - 8, bx + 78, by], fill=(220, 30, 50))
    d.rectangle([bx + 26, by - 8, bx + 48, by - 4], fill=(30, 70, 140))
    # ballot paper going in
    d.polygon([(bx + 28, by - 26), (bx + 46, by - 26), (bx + 46, by - 8),
               (bx + 28, by - 8)], fill=(255, 255, 255))
    d.line([bx + 31, by - 16, bx + 36, by - 11], fill=TEAL, width=3)
    d.line([bx + 36, by - 11, bx + 43, by - 22], fill=TEAL, width=3)
    d.text((x + 8, y + 6), "2027", font=F("sans_b", 16),
           fill=(255, 255, 255))
    d.text((x + w - 62, y + 6), "FEB 2027", font=F("sans_b", 9),
           fill=(200, 220, 255))
    chip(d, x, y + h - 16, w, "THIRD-TERM BID", (15, 45, 95))


ART = {1: art_kyiv, 2: art_cyclone, 3: art_cop31, 4: art_markets,
       5: art_space, 6: art_reset, 7: art_cpi, 8: art_rates,
       9: art_cricket, 10: art_pill, 11: art_boat, 12: art_strike,
       13: art_ballot}

# ------------------------------------------------------------ world map
# Dot-grid world map, 46 x 22 cells ('#' = land). Hand-built approximation.
WORLD = [
    ".####################...######################",
    ".####################....###.#################",
    "..##############.###...#######################",
    "...############.......########################",
    "....##########........######################..",
    ".....########.........##################......",
    "......######..........######.#########........",
    ".......#####..........########.#######........",
    "........####..........########..######........",
    ".........###..........########...#####........",
    "..........##.#######....########....####......",
    "............########....#######....###........",
    ".............#######....######....####........",
    ".............######.....#####....####...###...",
    "..............#####......####....###...#####..",
    "...............####.......###.....##...#####..",
    "................###........##...........####..",
    ".................##......................##...",
    "..................#...........................",
    "..............................................",
    "..............................................",
    "..............................................",
]

# pin number -> (x fraction, y fraction) on the map panel
PINS = {
    1: (0.615, 0.15), 2: (0.74, 0.42), 3: (0.60, 0.33), 4: (0.885, 0.27),
    6: (0.485, 0.13), 7: (0.83, 0.36), 8: (0.82, 0.25), 9: (0.96, 0.84),
    11: (0.45, 0.45), 12: (0.525, 0.26), 13: (0.25, 0.46),
}


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    rows, cols = len(WORLD), len(WORLD[0])
    cw, ch = w / cols, h / rows
    for r, row in enumerate(WORLD):
        for c, ch2 in enumerate(row):
            if ch2 == "#":
                cx, cy = x + (c + 0.5) * cw, y + (r + 0.5) * ch
                d.ellipse([cx - 1.6, cy - 1.6, cx + 1.6, cy + 1.6],
                          fill=(232, 217, 168))
    f = F("sans_b", 8)
    for n, (fx, fy) in PINS.items():
        cx, cy = x + fx * w, y + fy * h
        d.ellipse([cx - 6.5, cy - 6.5, cx + 6.5, cy + 6.5], fill=RED,
                  outline=(255, 255, 255), width=1)
        t = str(n)
        tw = d.textlength(t, font=f)
        d.text((cx - tw / 2, cy - 5.5), t, font=f, fill=(255, 255, 255))


# ------------------------------------------------------------ composition
TAG_COLOURS = {
    "REPORTED": (30, 122, 52), "CLAIM": (178, 34, 34),
    "FORECAST": (196, 106, 27), "ONGOING": (31, 78, 121),
    "EARLY TRIAL": (91, 91, 138), "ESTIMATE": (100, 100, 100),
    "OFFICIALS SAY": (15, 94, 92),
}


def tag_chip(d, x_right, y, tag, size=8):
    f = F("sans_b", size)
    tw = d.textlength(tag, font=f)
    w = tw + 10
    d.rectangle([x_right - w, y, x_right, y + size + 4], fill=TAG_COLOURS.get(
        tag, (100, 100, 100)))
    d.text((x_right - w + 5, y + 2), tag, font=f, fill=(255, 255, 255))
    return w


def story_card(d, x, y, w, h, story, lead=False):
    n, place, beat, tag, head, body = story
    art_h = 116 if lead else 72
    ART[n](d, x, y, w, art_h)
    ty = y + art_h + 5
    f_tag = F("sans_b", 10 if lead else 8)
    chip_size = 8 if lead else 7
    chip_w = d.textlength(tag, font=F("sans_b", chip_size)) + 10
    tag_txt = "%d \u00b7 %s \u2014 %s" % (n, place, beat)
    while (d.textlength(tag_txt, font=f_tag) > w - chip_w - 6
           and len(tag_txt) > 6):
        tag_txt = tag_txt[:-1]
    if tag_txt != "%d \u00b7 %s \u2014 %s" % (n, place, beat):
        tag_txt = tag_txt.rstrip(" .\u2014") + "\u2026"
    d.text((x, ty), tag_txt, font=f_tag, fill=RED)
    tag_chip(d, x + w, ty, tag, chip_size)
    hy = ty + (16 if lead else 13)
    f_head = F("serif_b", 18 if lead else 13)
    f_body = F("sans", 10 if lead else 9)
    nlines = text_block(d, x, hy, head, f_head, w, 2,
                        leading=22 if lead else 15)
    by = nlines + 2
    text_block(d, x, by, body, f_body, w, 3 if lead else 2,
               fill=(40, 40, 40), leading=13 if lead else 11.5)


def render(path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([6, 6, W - 7, H - 7], outline=INK, width=2)
    d.rectangle([10, 10, W - 11, H - 11], outline=INK, width=1)
    M, CW = 14, 996

    # top strap
    d.text((M, 12), "THE WORLD IN ONE DAY", font=F("sans_b", 11), fill=RED)
    rt = "FRIDAY'S NEWS \u00b7 ONE PAGE \u00b7 36 STORIES \u00b7 7 REGIONS"
    f_rt = F("sans_b", 10)
    d.text((M + CW - d.textlength(rt, font=f_rt), 13), rt, font=f_rt, fill=INK)
    d.line([M, 28, M + CW, 28], fill=INK, width=1)

    # masthead
    f_m = F("mast", 52)
    title = "Friday 20 November 2026"
    d.text(((W - d.textlength(title, font=f_m)) / 2, 30), title, font=f_m,
           fill=INK)
    f_sub = F("serif_i", 15)
    sub = ("Russian missiles hit Kyiv's bridges \u00b7 Cyclone Akvan makes "
           "landfall \u00b7 COP31 ends deadlocked \u00b7 Asia's markets plunge")
    d.text(((W - d.textlength(sub, font=f_sub)) / 2, 92), sub, font=f_sub,
           fill=DARKRED)
    d.line([M, 112, M + CW, 112], fill=INK, width=2)
    d.line([M, 116, M + CW, 116], fill=INK, width=1)

    # numbers strip
    ny, nh = 120, 44
    cw6 = CW / 6
    for i, (num, cap) in enumerate(NUMBERS):
        cx = M + i * cw6
        d.text((cx + 4, ny), num, font=F("sans_b", 21),
               fill=RED if i in (0, 2, 5) else INK)
        text_block(d, cx + 4, ny + 24, cap, F("sans", 9), cw6 - 10, 2,
                   fill=GRAY, leading=11)
        if i:
            d.line([cx, ny + 2, cx, ny + nh - 2], fill=LIGHTGRAY, width=1)
    d.line([M, ny + nh + 2, M + CW, ny + nh + 2], fill=INK, width=1)

    # region bar
    ry, rh = 169, 18
    rx = M
    f_rb = F("sans_b", 10)
    for label, count, col in REGIONS:
        seg = CW * count / 36
        d.rectangle([rx, ry, rx + seg, ry + rh], fill=col)
        tw = d.textlength(label, font=f_rb)
        d.text((rx + (seg - tw) / 2, ry + 4), label, font=f_rb,
               fill=(255, 255, 255))
        rx += seg

    # lead row: 3 cards of 322 + 2 gaps of 15
    ly, lh = 193, 206
    for i, story in enumerate(LEAD):
        story_card(d, M + i * (322 + 15), ly, 322, lh, story, lead=True)

    # feature rows: 5 cards of 192 + 4 gaps of 9
    for row in range(2):
        fy = 405 + row * 152
        for i, story in enumerate(FEATURE[row * 5:(row + 1) * 5]):
            story_card(d, M + i * (192 + 9), fy, 192, 150, story)

    # bottom: map left, briefs right
    by0 = 713
    d.text((M, by0), "WHERE IT HAPPENED", font=F("sans_b", 11), fill=INK)
    d.line([M, by0 + 15, M + 330, by0 + 15], fill=INK, width=1)
    draw_map(d, M, by0 + 18, 330, 158)
    d.text((M, by0 + 180), "Pins 1-13 mark the illustrated stories.",
           font=F("sans", 8.5), fill=GRAY)
    d.text((M, by0 + 191), "5 SPACE \u2014 Mercury \u00b7 10 WORLD \u2014 health trial.",
           font=F("sans", 8.5), fill=GRAY)

    bx = M + 340
    bw = CW - 340
    d.text((bx, by0), "ALSO ON FRIDAY 20 NOVEMBER \u2014 23 MORE STORIES",
           font=F("sans_b", 11), fill=INK)
    d.line([bx, by0 + 15, bx + bw, by0 + 15], fill=INK, width=1)
    f_bn = F("sans_b", 9.5)
    f_bt = F("sans", 9.5)
    col_w = (bw - 12) / 2
    for idx, (n, place, text) in enumerate(BRIEFS):
        col, row = idx // 12, idx % 12
        px = bx + col * (col_w + 12)
        py = by0 + 20 + row * 15.5
        head = "%d %s " % (n, place)
        hw = d.textlength(head, font=f_bn)
        d.text((px, py), head, font=f_bn, fill=RED)
        # trim body to fit the column
        rest = text
        while rest and d.textlength(rest, font=f_bt) > col_w - hw:
            rest = rest[:-1]
        if rest != text:
            rest = rest.rstrip(" .,;:") + "\u2026"
        d.text((px + hw, py), rest, font=f_bt, fill=INK)

    # date check
    dy = 931
    d.rectangle([M, dy, M + CW, dy + 38], outline=RED, width=2)
    d.text((M + 6, dy + 4), "DATE CHECK", font=F("sans_b", 10), fill=RED)
    f_dc = F("sans", 9.5)
    dw = d.textlength("DATE CHECK  ", font=F("sans_b", 10))
    lines = wrap(d, DATE_CHECK, f_dc, CW - dw - 16)
    for i, line in enumerate(lines[:2]):
        d.text((M + 6 + dw, dy + 4 + i * 13), line, font=f_dc, fill=INK)

    # footer
    text_block(d, M, 975, FOOTER, F("sans", 8.5), CW, 2, fill=GRAY,
               leading=10.5)

    img.save(path, "PNG", optimize=True)
    return path


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    render(out)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
