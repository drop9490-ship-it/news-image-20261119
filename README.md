# news-image-20261119

One-page newspaper image summing up Thursday, 19 November 2026 — built for
the make.fun `news-image-20261119` competition ($250, free entry).

## What it is

`render.py` (Python + Pillow, no other dependencies) draws a single
1024×1024 PNG newspaper page and writes it to `/output/entry.png` (a copy
is also saved as `entry.png` next to the script).

Layout: masthead, giant date title, lead story (Trump–Xi–Putin trilateral
summit in Shenzhen) with a drawn skyline illustration, three featured
stories (Anthropic's Nasdaq debut, Hakeem Jeffries for Speaker, GTA VI)
with two more drawn illustrations, a BY THE NUMBERS strip, a 24-story grid,
a dotted world map with a continent count, an ALSO ON list, and a JUDGE NOTE.

35 verified 19 November 2026 stories, each sourced from reporting published
on 19 Nov 2026 (AP, BBC, NDTV, Reuters, TheStreet, Renaissance Capital,
Investors.com, The Hindu, Space/Nature, USA Today, CNN, FT via reports).

## Run

```bash
python3 render.py
# writes /output/entry.png (and entry.png beside the script)
```

The render is deterministic (no randomness, no timestamps, fixed fonts),
so repeated runs produce byte-identical output.
