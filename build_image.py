#!/usr/bin/env python3
"""Draw the 26 November 2026 world-news front page.

One deterministic picture, 1024 x 1024, built only from the Python
standard library and Pillow. No network, no clock, no randomness
beyond a fixed seed, so two runs write identical bytes.

Layout, top to bottom:
  masthead with the date, a hero panel about the first Pakistani
  astronaut reaching Tiangong, a markets panel, a four-cell data
  strip, two columns of short stories, and a ticker along the foot.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

NAVY = (10, 26, 50)
PANEL = (19, 43, 82)
PANEL_EDGE = (58, 96, 148)
INK = (242, 239, 230)
MUTED = (159, 179, 206)
AMBER = (245, 166, 35)
RED = (214, 69, 65)
TEAL = (84, 190, 178)
FAINT = (122, 143, 173)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)


def wrap(draw, text, fnt, width):
    """Greedy word wrap returning a list of lines that fit width."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, fill, width, leading=None):
    """Draw wrapped text, return the y just below the last line."""
    leading = leading or int(fnt.size * 1.32)
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def wobbly_rect(draw, box, outline, width=2, seed=7, amp=1.6):
    """A rectangle whose edges jitter a little, like a hand-drawn frame."""
    rng = random.Random(seed)
    x0, y0, x1, y1 = box
    steps = 26
    top = [(x0 + (x1 - x0) * i / steps, y0 + rng.uniform(-amp, amp))
           for i in range(steps + 1)]
    right = [(x1 + rng.uniform(-amp, amp), y0 + (y1 - y0) * i / steps)
             for i in range(steps + 1)]
    bottom = [(x1 - (x1 - x0) * i / steps, y1 + rng.uniform(-amp, amp))
              for i in range(steps + 1)]
    left = [(x0 + rng.uniform(-amp, amp), y1 - (y1 - y0) * i / steps)
            for i in range(steps + 1)]
    for pts in (top, right, bottom, left):
        draw.line(pts, fill=outline, width=width, joint="curve")


def starfield(draw, box, seed=11, count=90):
    rng = random.Random(seed)
    x0, y0, x1, y1 = box
    for _ in range(count):
        x = rng.uniform(x0, x1)
        y = rng.uniform(y0, y1)
        r = rng.choice([1, 1, 1, 2])
        shade = rng.randint(200, 245)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(shade, shade, 245))


def draw_station(draw, cx, cy, scale=1.0):
    """Stylised Tiangong: a core module, two solar wings, a docking node."""
    # solar wings
    wing_w, wing_h = int(150 * scale), int(26 * scale)
    for side in (-1, 1):
        x0 = cx + side * int(46 * scale) if side > 0 else cx - side * int(46 * scale) - wing_w
        x1 = x0 + wing_w
        y0, y1 = cy - wing_h // 2, cy + wing_h // 2
        draw.rectangle([x0, y0, x1, y1], fill=(38, 74, 128),
                       outline=AMBER, width=2)
        for i in range(1, 6):
            gx = x0 + wing_w * i / 6
            draw.line([(gx, y0), (gx, y1)], fill=AMBER, width=1)
        draw.line([(x0, cy), (x1, cy)], fill=(120, 150, 190), width=1)
    # core module
    mw, mh = int(92 * scale), int(34 * scale)
    draw.rounded_rectangle([cx - mw // 2, cy - mh // 2,
                            cx + mw // 2, cy + mh // 2],
                           radius=int(12 * scale), fill=INK,
                           outline=AMBER, width=2)
    # docking node + small module below
    draw.ellipse([cx - int(13 * scale), cy + mh // 2 - 4,
                  cx + int(13 * scale), cy + mh // 2 + int(20 * scale)],
                 fill=TEAL, outline=INK, width=2)
    # windows
    for dx in (-28, 0, 28):
        draw.ellipse([cx + dx * scale - 4, cy - 4,
                      cx + dx * scale + 4, cy + 4], fill=NAVY)


def draw_rocket_arc(draw, box):
    """A dashed ascent arc with a small rocket at its head."""
    x0, y0, x1, y1 = box
    pts = []
    for i in range(41):
        t = i / 40
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t * t
        pts.append((x, y))
    for i in range(0, len(pts) - 1, 2):
        draw.line([pts[i], pts[i + 1]], fill=AMBER, width=2)
    hx, hy = pts[-1]
    draw.polygon([(hx, hy - 14), (hx - 6, hy + 6), (hx + 6, hy + 6)],
                 fill=RED, outline=INK)
    draw.rectangle([hx - 6, hy + 6, hx + 6, hy + 14], fill=INK)
    for dx in (-8, 8):
        draw.polygon([(hx + dx, hy + 8), (hx + dx * 1.6, hy + 18),
                      (hx + dx * 0.6, hy + 14)], fill=AMBER)


def draw_chart(draw, box, values, colour):
    """A small jagged line chart inside box, values normalised."""
    x0, y0, x1, y1 = box
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1
    pts = []
    for i, v in enumerate(values):
        x = x0 + (x1 - x0) * i / (len(values) - 1)
        y = y1 - (y1 - y0) * (v - lo) / span
        pts.append((x, y))
    draw.line(pts, fill=colour, width=3, joint="curve")
    draw.ellipse([pts[-1][0] - 4, pts[-1][1] - 4,
                  pts[-1][0] + 4, pts[-1][1] + 4], fill=colour)
    return pts


def kicker(draw, x, y, text, colour=AMBER):
    f = SANS_B(17)
    draw.text((x, y), text, font=f, fill=colour)
    return draw.textlength(text, font=f)


def build():
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)

    # faint dotted texture across the whole page
    rng = random.Random(3)
    for _ in range(240):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        d.point((x, y), fill=(24, 46, 84))

    # ---- masthead -------------------------------------------------
    d.text((48, 26), "THE WORLD IN ONE DAY", font=SERIF_B(54), fill=INK)
    d.text((48, 96), "THURSDAY  \u00b7  26 NOVEMBER 2026",
           font=SANS_B(24), fill=AMBER)
    d.text((48, 128), "The day's world news, drawn in one picture",
           font=SERIF(20), fill=MUTED)
    d.line([(48, 162), (976, 162)], fill=AMBER, width=3)
    d.line([(48, 168), (976, 168)], fill=PANEL_EDGE, width=1)

    # ---- hero: first Pakistani in orbit ---------------------------
    hx0, hy0, hx1, hy1 = 48, 184, 640, 520
    d.rounded_rectangle([hx0, hy0, hx1, hy1], radius=10,
                        fill=PANEL, outline=PANEL_EDGE, width=2)
    starfield(d, (hx0 + 8, hy0 + 8, hx1 - 8, hy0 + 150), seed=21, count=70)
    draw_station(d, 340, 262, scale=1.0)
    draw_rocket_arc(d, (90, 330, 250, 215))
    d.text((hx0 + 20, hy0 + 158), "1st", font=SERIF_B(96), fill=AMBER)
    d.text((hx0 + 196, hy0 + 178), "FOREIGN ASTRONAUT\nABOARD TIANGONG",
           font=SANS_B(28), fill=INK)
    para(d, hx0 + 20, hy0 + 260,
         "Shenzhou-24 docks at Tiangong with Muhammad Zeeshan Ali "
         "\u2014 the first Pakistani in orbit, and the first foreigner "
         "aboard China's station.", SANS(20), INK, hx1 - hx0 - 40,
         leading=25)

    # ---- markets panel --------------------------------------------
    mx0, my0, mx1, my1 = 664, 184, 976, 520
    d.rounded_rectangle([mx0, my0, mx1, my1], radius=10,
                        fill=PANEL, outline=PANEL_EDGE, width=2)
    wobbly_rect(d, (mx0, my0, mx1, my1), RED, width=2, seed=5)
    d.text((mx0 + 20, my0 + 16), "MARKETS IN RETREAT", font=SANS_B(22),
           fill=RED)
    draw_chart(d, (mx0 + 20, my0 + 56, mx1 - 20, my0 + 132),
               [100, 97, 99, 94, 96, 91, 93, 88], RED)
    rows = [
        ("Nasdaq 100", "\u22120.6%", RED),
        ("S&P 500", "\u22120.3%", RED),
        ("Dow Jones", "+0.3%", TEAL),
        ("Stoxx 600", "\u22121.1%", RED),
    ]
    y = my0 + 148
    for name, val, col in rows:
        d.text((mx0 + 20, y), name, font=SANS(20), fill=INK)
        vw = d.textlength(val, font=SANS_B(20))
        d.text((mx1 - 20 - vw, y), val, font=SANS_B(20), fill=col)
        y += 31
    para(d, mx0 + 20, y + 4,
         "Tariff fears and an AI sell-off sweep Wall Street.",
         SANS(17), MUTED, mx1 - mx0 - 40, leading=22)

    # ---- data strip ------------------------------------------------
    sy0, sy1 = 536, 636
    cells = [
        ("31", "KILLED IN CAIRO", "Tanker crash fire on\nthe ring road"),
        ("+36%", "BANGLADESH PAY RISE", "Garment workers win\na wage rise"),
        ("10", "YEARS OF PEACE", "Colombia marks a decade\nsince its peace deal"),
        ("$237.5B", "VENEZUELA DEBT", "Caracas reveals its\npublic debt pile"),
    ]
    cw = (976 - 48) / 4
    for i, (num, label, sub) in enumerate(cells):
        x0 = 48 + cw * i
        d.rectangle([x0 + 2, sy0, x0 + cw - 2, sy1], fill=(13, 33, 64),
                    outline=PANEL_EDGE, width=1)
        d.text((x0 + 18, sy0 + 8), num, font=SERIF_B(36),
               fill=AMBER if i != 2 else TEAL)
        d.text((x0 + 18, sy0 + 48), label, font=SANS_B(15), fill=INK)
        para(d, x0 + 18, sy0 + 66, sub, SANS(14), MUTED,
             cw - 36, leading=16)

    # ---- two columns of short stories -----------------------------
    cy = 652
    d.text((48, cy), "THE REST OF THE DAY", font=SANS_B(20), fill=AMBER)
    d.line([(48, cy + 30), (976, cy + 30)], fill=PANEL_EDGE, width=1)
    stories_l = [
        ("TARIFFS", "US unveils new Section 301 duties on 14 partners; "
         "China hit hardest, near 45%."),
        ("BRAZIL", "Petrobras unveils a US$122 billion investment plan, "
         "its biggest in years."),
        ("INDIA", "Constitution Day: IITs to add 6,000 seats in robotics, "
         "AI and space."),
    ]
    stories_r = [
        ("ISRAEL", "Judges recommend dropping the most serious charges "
         "against Netanyahu."),
        ("KOREA", "North Korea expels a Swiss diplomat and orders "
         "Switzerland's new Pyongyang office shut."),
        ("UKRAINE", "Kyiv widens naval strikes; Moscow says talks with "
         "Washington continue."),
    ]
    y = cy + 44
    for col_x, stories in ((48, stories_l), (512, stories_r)):
        yy = y
        for tag, text in stories:
            kicker(d, col_x, yy, tag)
            yy = para(d, col_x, yy + 22, text, SANS(18), INK,
                      440, leading=23)
            yy += 10
    # ---- ticker ---------------------------------------------------
    ty0, ty1 = 952, 1000
    d.rectangle([0, ty0, W, ty1], fill=(8, 20, 40))
    d.line([(0, ty0), (W, ty0)], fill=AMBER, width=2)
    ticker = ("CAIRO FIRE: 31 DEAD  \u00b7  SHENZHOU-24: 90+ EXPERIMENTS  "
              "\u00b7  US PCE 3.8%  \u00b7  BRENT $94.36")
    tsize = 17
    while d.textlength(ticker, font=SANS_B(tsize)) > W - 96 and tsize > 10:
        tsize -= 1
    d.text((48, ty0 + 14), ticker, font=SANS_B(tsize), fill=AMBER)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, format="PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    build()
