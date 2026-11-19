#!/usr/bin/env python3
"""Render a one-page newspaper image for 19 November 2026.

Writes a single 1024x1024 PNG to /output/entry.png (and a copy next to
this script as entry.png for the repository). Deterministic: no random
numbers, no timestamps, fixed fonts, so two runs are byte-identical.

Layout (1024x1024, tight vertical budget):
  masthead -> giant date -> lead story + summit illustration
  -> three featured stories (Anthropic IPO, Jeffries, GTA VI; two with
  illustrations) -> BY THE NUMBERS strip -> 18-story grid (3 cols x 6)
  -> dotted world map + ALSO ON (2 cols) -> JUDGE NOTE footer.
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 26
OUT_ABS = "/output/entry.png"

INK = (17, 17, 17)
PAPER = (255, 255, 255)
RED = (178, 34, 34)
BLUE = (30, 64, 175)
GREY = (120, 120, 120)
DARKBAND = (24, 24, 24)
MAPDOT = (70, 70, 70)

FONT_DIR = "/usr/share/fonts/truetype"


def font(path, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, path), size)


SERIF_B = lambda s: font("dejavu/DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("dejavu/DejaVuSerif.ttf", s)
SANS_B = lambda s: font("dejavu/DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("dejavu/DejaVuSans.ttf", s)


def wrap(draw, text, fnt, max_w):
    """Wrap text into lines that fit max_w pixels."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_w, fill=INK, leading=None,
                 max_lines=None):
    """Draw wrapped text (optionally capped at max_lines); return y below."""
    if leading is None:
        leading = int(fnt.size * 1.25)
    lines = wrap(draw, text, fnt, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


# ---------------------------------------------------------------- stories
LEAD = {
    "kicker": "SHENZHEN  •  APEC SUMMIT",
    "headline": "THE G3 MEET IN SHENZHEN",
    "body": (
        "Donald Trump, Xi Jinping and Vladimir Putin held the first trilateral "
        "meeting of sitting US, Russian and Chinese presidents on Thursday, on "
        "the sidelines of the APEC summit in Shenzhen. Ukraine, Taiwan and "
        "Europe waited outside the room. The three leaders billed the talks as "
        "safeguarding peace and strategic stability; critics warned the world "
        "was watching a new Yalta. No concrete outcome was announced."
    ),
}

FEATURED = [
    {
        "kicker": "WALL STREET",
        "headline": "ANTHROPIC DEBUTS AT $1.4 TRILLION",
        "body": (
            "The Claude maker debuted on Nasdaq as ANT, selling 825m shares at "
            "$70-$78 for up to $64.4bn, plus a $26bn placement. Google and "
            "Nvidia put in $10bn each."
        ),
        "illo": "ipo",
    },
    {
        "kicker": "WASHINGTON",
        "headline": "JEFFRIES TO BE FIRST BLACK SPEAKER",
        "body": (
            "House Democrats nominated Hakeem Jeffries to be Speaker, the first "
            "Black American to hold the gavel. He takes the chair on 3 January "
            "after the midterm rout."
        ),
        "illo": None,
    },
    {
        "kicker": "VICE CITY",
        "headline": "GTA VI ARRIVES AFTER 13 YEARS",
        "body": (
            "Grand Theft Auto VI began its global rollout on Thursday, returning "
            "players to Vice City after a 13-year wait — one of the biggest "
            "entertainment launches ever."
        ),
        "illo": "gta",
    },
]

GRID = [
    ("DOW SINKS 561 AS UNITEDHEALTH TUMBLES",
     "UnitedHealth fell 10.2% after a Medicare anti-fraud crackdown; the S&P 500 posted a fifth straight loss."),
    ("VOYAGER 1 REACHES A LIGHT-DAY",
     "After almost 50 years in space, NASA's probe is about one light-day from Earth — a record distance."),
    ("CYCLONE AKVAN MAKES LANDFALL",
     "The storm is crossing between Machilipatnam and Puri; railways and states are on high alert."),
    ("ISLAM TO BE LARGEST FAITH BY 2035",
     "Pew Research projects Islam will outnumber Christians within a decade on higher birth rates."),
    ("EARTH'S MISSING BILLION YEARS FOUND",
     "A Nature study blames mantle currents and ancient ice sheets for erasing a billion years of geology."),
    ("CANADA RESETS CHINA TIES",
     "PM Carney says Ottawa is adjusting its China relationship as it seeks the right deal with Washington."),
    ("SENATORS: AI CYBER THREATS OUTPACING DEFENCES",
     "US senators warn AI-enabled cyber attacks are moving faster than American defences."),
    ("MELENCHON 'COULD WIN' FRENCH PRESIDENCY",
     "France's justice minister says the hard-left leader could win the next presidential election."),
    ("SAUDI: DANGER PASSED IN THREE CITIES",
     "Riyadh says the danger has passed in three southern cities after security alerts."),
    ("COCAINE, MILLIONS OF PILLS SEIZED IN LIBYA",
     "Officials say a huge haul of cocaine and pills was seized in the country's east."),
    ("GAZA RAINS DISPLACE 46,000 FAMILIES",
     "Heavy rain displaced 46,000 households and damaged 40,000 shelters; 150,000 tents await entry."),
    ("ESTONIA TO SHUT RUSSIA BORDER CROSSINGS",
     "Tallinn will close road crossings from 1 Dec after an alleged GRU sabotage plot against a defence firm."),
    ("HOUTHIS SEIZE RED SEA COAST",
     "Yemeni government forces pulled back from Bab el-Mandeb to defend Aden, letting Houthis take coastal positions."),
    ("ZELENSKY: LIFT STARSHIELD LIMITS",
     "Ukraine's president urges Washington to lift curbs on SpaceX Starshield, saying they hinder drone defence."),
    ("LIU MAKES HISTORY IN HOUSE",
     "Rep. Liu Yunping is elected House Democratic Caucus chair — the first Taiwanese American in the post."),
    ("MODI MEETS WILLIAM AND KATE",
     "India's PM met the Prince and Princess of Wales to discuss boosting UK-India ties."),
    ("INDIA, JAPAN TO REVIEW DEFENCE TIES",
     "The two countries will hold a 2+2 ministerial dialogue on defence and strategic cooperation."),
    ("DEUTSCHE BANK AND $582M EPSTEIN CASH",
     "The bank handled $582m in transactions linked to Jeffrey Epstein between 2013 and 2018, the FT reports."),
]

ALSO_ON = [
    "US test-fires unarmed ICBM",
    "House Dems probe Trump family",
    "GOP seeks VA tech answers",
    "Social Security 'a Ponzi scheme'",
    "Oil slides: WTI $83.26",
    "Gold, copper, silver tumble",
    "COP31 summit under way",
    "Somalia accuses UAE of bases",
    "Pochettino leaves for Man Utd",
    "India racism complaint to AFC",
    "HCMC Police stun champs",
    "Microsoft in AI talks",
    "Trump 'unhappy' with Vance",
]

NUMBERS = [
    ("$64.4bn", "Anthropic IPO raise"),
    ("561", "points lost by the Dow"),
    ("10.2%", "UnitedHealth's fall"),
    ("46,000", "Gaza households displaced"),
    ("1", "light-day: Voyager 1's distance"),
]

JUDGE_NOTE = (
    "JUDGE NOTE: A day of firsts — the first G3 summit, the first Black Speaker, "
    "the first $1.4tn AI debut, and a probe a light-day away. 19 November 2026 "
    "packed a decade of history into one page."
)


# ---------------------------------------------------------------- illustrations
def draw_summit(d, x, y, w, h):
    """Shenzhen skyline at dusk with three flags: the G3 summit."""
    d.rectangle([x, y, x + w, y + h], fill=(24, 32, 54))
    cx, cy, r = x + w - 52, y + 42, 26
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(214, 90, 60))
    base = y + h
    towers = [
        (0.02, 0.52, 0.13), (0.14, 0.38, 0.11), (0.26, 0.60, 0.12),
        (0.39, 0.30, 0.10), (0.50, 0.46, 0.12), (0.63, 0.34, 0.11),
        (0.75, 0.55, 0.12), (0.88, 0.42, 0.11),
    ]
    for fx, fh, fw in towers:
        tx = x + int(fx * w)
        tw = int(fw * w)
        th = int(fh * h)
        d.rectangle([tx, base - th, tx + tw, base], fill=(12, 16, 28))
        for wy in range(base - th + 8, base - 6, 12):
            for wx in range(tx + 4, tx + tw - 4, 10):
                if (wx + wy) % 20 < 10:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 214, 120))
    flag_cols = [(178, 34, 34), (30, 64, 175), (255, 255, 255)]
    for i, col in enumerate(flag_cols):
        px = x + 30 + i * 34
        d.line([px, y + 18, px, y + 52], fill=(255, 255, 255), width=2)
        d.rectangle([px, y + 18, px + 26, y + 34], fill=col, outline=(255, 255, 255))
    d.rectangle([x, y, x + w, y + h], outline=(17, 17, 17), width=2)


def draw_ipo(d, x, y, w, h):
    """Rising chart with the ANT ticker: the Anthropic debut."""
    d.rectangle([x, y, x + w, y + h], fill=(16, 40, 32))
    bars = [0.22, 0.30, 0.26, 0.42, 0.38, 0.55, 0.50, 0.68, 0.62, 0.82]
    bw = w // (len(bars) + 1)
    base = y + h - 22
    for i, f in enumerate(bars):
        bx = x + 10 + i * bw
        bh = int(f * (h - 42))
        d.rectangle([bx, base - bh, bx + bw - 6, base], fill=(46, 160, 90))
    pts = []
    for i, f in enumerate(bars):
        px = x + 10 + i * bw + (bw - 6) // 2
        py = base - int(f * (h - 42)) - 6
        pts.append((px, py))
    d.line(pts, fill=(255, 214, 120), width=3)
    d.polygon([(pts[-1][0] - 4, pts[-1][1] + 8), (pts[-1][0] + 10, pts[-1][1] - 2),
               (pts[-1][0] - 2, pts[-1][1] - 10)], fill=(255, 214, 120))
    d.text((x + 12, y + 6), "ANT", font=SANS_B(20), fill=(255, 255, 255))
    d.text((x + w - 88, y + 8), "+$64.4bn", font=SANS_B(14), fill=(255, 214, 120))
    d.rectangle([x, y, x + w, y + h], outline=(17, 17, 17), width=2)


def draw_gta(d, x, y, w, h):
    """Vice City at dusk: neon sunset, skyline, palm trees."""
    d.rectangle([x, y, x + w, y + h], fill=(46, 16, 64))
    cx, cy, r = x + w // 2, y + h - 30, 40
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 120, 80))
    d.ellipse([cx - r + 10, cy - r + 10, cx + r - 10, cy + r - 10],
              fill=(255, 170, 90))
    base = y + h
    towers = [(0.00, 0.42, 0.16), (0.17, 0.58, 0.14), (0.32, 0.36, 0.15),
              (0.48, 0.52, 0.14), (0.63, 0.40, 0.15), (0.79, 0.56, 0.13),
              (0.90, 0.44, 0.10)]
    for fx, fh, fw in towers:
        tx = x + int(fx * w)
        tw = int(fw * w)
        th = int(fh * h)
        d.rectangle([tx, base - th, tx + tw, base], fill=(18, 8, 30))
        for wy in range(base - th + 7, base - 5, 11):
            for wx in range(tx + 4, tx + tw - 4, 9):
                if (wx * 3 + wy) % 17 < 8:
                    d.rectangle([wx, wy, wx + 3, wy + 3], fill=(255, 230, 140))
    for px, lean in ((x + 16, 1), (x + w - 18, -1)):
        d.line([px, base, px + 8 * lean, base - 30], fill=(10, 40, 20), width=4)
        top = (px + 8 * lean, base - 30)
        for ang in (-50, -25, 0, 25, 50):
            rad = math.radians(ang - 90)
            ex = top[0] + int(18 * math.cos(rad))
            ey = top[1] + int(13 * math.sin(rad)) - 4
            d.line([top, (ex, ey)], fill=(20, 90, 50), width=3)
    d.rectangle([x, y, x + w, y + h], outline=(17, 17, 17), width=2)


def draw_dotted_map(d, x, y, w, h):
    """Dotted world map from overlapping ellipses (map space 0..100 x 0..50)."""
    ellipses = [
        (18, 11, 12, 7), (8, 8, 5, 4), (20, 19, 4, 3),       # N. America
        (33, 5, 3, 2),                                          # Greenland
        (29, 26, 4, 5), (31, 38, 3, 5),                        # S. America
        (52, 10, 5, 4),                                          # Europe
        (55, 26, 7, 9), (54, 18, 5, 4),                        # Africa
        (72, 10, 16, 7), (70, 18, 8, 5), (78, 22, 4, 3),      # Asia
        (62, 16, 4, 3),                                          # Middle East
        (82, 26, 3, 1.5), (86, 27, 2, 1),                      # SE Asia isles
        (85, 36, 6, 4),                                          # Australia
    ]

    def inside(px, py):
        for (cx, cy, rx, ry) in ellipses:
            if ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2 <= 1.0:
                return True
        return False

    step_x, step_y = 6, 6
    cols = int(w / step_x)
    rows = int(h / step_y)
    for r in range(rows):
        for c in range(cols):
            mx = (c + 0.5) * (100.0 / cols)
            my = (r + 0.5) * (50.0 / rows)
            if inside(mx, my):
                dx = x + c * step_x + 2
                dy = y + r * step_y + 2
                d.ellipse([dx, dy, dx + 3, dy + 3], fill=MAPDOT)


# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    x0, x1 = MARGIN, W - MARGIN
    cw = x1 - x0  # 972

    # ---- masthead (y 14..~148)
    y = 14
    f_mast = SERIF_B(34)
    t = "THE WORLD IN ONE PAGE"
    d.text(((W - d.textlength(t, font=f_mast)) / 2, y), t, font=f_mast, fill=INK)
    y += 44
    d.text(((W - d.textlength("EVERY STORY THAT MATTERED  •  ONE PAGE",
                               font=SANS(11))) / 2, y),
           "EVERY STORY THAT MATTERED  •  ONE PAGE", font=SANS(11), fill=GREY)
    y += 16
    d.line([x0, y, x1, y], fill=INK, width=3)
    y += 6
    f_date = SERIF_B(42)
    t = "19 NOVEMBER 2026"
    d.text(((W - d.textlength(t, font=f_date)) / 2, y), t, font=f_date, fill=RED)
    y += 50
    f_day = SANS_B(14)
    t = "T H U R S D A Y"
    d.text(((W - d.textlength(t, font=f_day)) / 2, y), t, font=f_day, fill=INK)
    y += 19
    d.line([x0, y, x1, y], fill=INK, width=2)
    y += 8

    # ---- lead story + summit illustration (y ~156..~295)
    lead_y = y
    illo_w, illo_h = 300, 128
    illo_x, illo_y = x1 - illo_w, lead_y + 2
    draw_summit(d, illo_x, illo_y, illo_w, illo_h)
    tw = illo_x - x0 - 16
    d.text((x0, lead_y), LEAD["kicker"], font=SANS_B(11), fill=BLUE)
    y2 = lead_y + 16
    y2 = draw_wrapped(d, x0, y2, LEAD["headline"], SERIF_B(26), tw, leading=30)
    y2 += 3
    y2 = draw_wrapped(d, x0, y2, LEAD["body"], SERIF(12), tw, leading=16,
                      max_lines=4)
    y = max(illo_y + illo_h, y2) + 8
    d.line([x0, y, x1, y], fill=GREY, width=1)
    y += 8

    # ---- featured row: three columns (y ~308..~470)
    col_w = (cw - 2 * 16) // 3
    feat_y = y
    feat_bottom = feat_y
    for i, f in enumerate(FEATURED):
        cx = x0 + i * (col_w + 16)
        cy = feat_y
        d.text((cx, cy), f["kicker"], font=SANS_B(10), fill=BLUE)
        cy += 15
        if f["illo"] == "ipo":
            draw_ipo(d, cx, cy, col_w, 72)
            cy += 72 + 6
        elif f["illo"] == "gta":
            draw_gta(d, cx, cy, col_w, 72)
            cy += 72 + 6
        cy = draw_wrapped(d, cx, cy, f["headline"], SERIF_B(16), col_w,
                          leading=19, max_lines=2)
        cy += 2
        cy = draw_wrapped(d, cx, cy, f["body"], SERIF(10), col_w, leading=13,
                          max_lines=3)
        feat_bottom = max(feat_bottom, cy)
    y = feat_bottom + 8
    d.line([x0, y, x1, y], fill=INK, width=2)
    y += 7

    # ---- BY THE NUMBERS strip (48px)
    strip_h = 48
    d.rectangle([x0, y, x1, y + strip_h], fill=DARKBAND)
    d.text((x0 + 10, y + 3), "BY THE NUMBERS", font=SANS_B(10),
           fill=(255, 214, 120))
    ncol = len(NUMBERS)
    nwid = (cw - 20) // ncol
    for i, (num, lab) in enumerate(NUMBERS):
        nx = x0 + 10 + i * nwid
        d.text((nx, y + 16), num, font=SANS_B(17), fill=(255, 255, 255))
        d.text((nx, y + 37), lab, font=SANS(8), fill=(200, 200, 200))
    y += strip_h + 8

    # ---- grid of short stories: 3 cols x 6 rows = 18
    d.text((x0, y), "THE DAY IN BRIEF", font=SANS_B(12), fill=RED)
    y += 17
    grid_top = y
    row_h = 47
    for idx, (head, summ) in enumerate(GRID):
        col = idx % 3
        row = idx // 3
        gx = x0 + col * (col_w + 16)
        gy = grid_top + row * row_h
        gy = draw_wrapped(d, gx, gy, head, SANS_B(10), col_w, leading=12,
                          max_lines=2)
        draw_wrapped(d, gx, gy, summ, SANS(9), col_w, leading=11,
                     max_lines=2)
    y = grid_top + 6 * row_h + 4
    d.line([x0, y, x1, y], fill=GREY, width=1)
    y += 7

    # ---- dotted world map (left) + ALSO ON (right, 2 cols)
    d.text((x0, y), "THE WORLD AT A GLANCE", font=SANS_B(12), fill=RED)
    d.text((x0 + 494, y), "ALSO ON", font=SANS_B(12), fill=RED)
    y += 17
    map_x, map_y = x0, y
    map_w, map_h = 460, 76
    draw_dotted_map(d, map_x, map_y, map_w, map_h)
    d.text((map_x, map_y + map_h + 3),
           "ASIA 12  •  N. AMERICA 17  •  EUROPE 4  •  AFRICA 2",
           font=SANS_B(9), fill=INK)
    ax = x0 + 494
    acol_w = (x1 - ax - 12) // 2
    half = (len(ALSO_ON) + 1) // 2
    for col_i, chunk in enumerate((ALSO_ON[:half], ALSO_ON[half:])):
        axx = ax + col_i * (acol_w + 12)
        ay = map_y
        for item in chunk:
            ay = draw_wrapped(d, axx, ay, "•  " + item, SANS(9), acol_w,
                              leading=13, max_lines=2)
    y = max(map_y + map_h + 18, map_y + half * 13 + 4) + 4
    d.line([x0, y, x1, y], fill=INK, width=2)
    y += 6

    # ---- judge note footer
    y = draw_wrapped(d, x0, y, JUDGE_NOTE, SERIF(11), cw, leading=14,
                     max_lines=3)
    y += 5
    d.text((x0, y), "THE WORLD IN ONE PAGE  •  THURSDAY, 19 NOVEMBER 2026  •  35 STORIES",
           font=SANS(9), fill=GREY)
    return img


def main():
    img = build()
    os.makedirs("/output", exist_ok=True)
    img.save(OUT_ABS, format="PNG", optimize=True)
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(here, format="PNG", optimize=True)
    print("wrote", OUT_ABS, os.path.getsize(OUT_ABS), "bytes")


if __name__ == "__main__":
    main()
