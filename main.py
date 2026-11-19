#!/usr/bin/env python3
"""Entrypoint for the news-image-20261119 entry.

Copies the front page built by render.py (entry.png, next to this file)
into the output directory. The directory comes from MAKEFUN_OUTPUT_DIR
and defaults to /output; it is created when it does not exist yet.

Round 1 ran render.py on the grading server and FAILED there (the
server has no PIL / DejaVu fonts), so the render step now happens
offline before submit and this entrypoint only copies the finished
1024x1024 image — the same copy pattern as news-image-20261118 v3.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    source = os.path.join(HERE, "entry.png")
    if not os.path.isfile(source):
        raise SystemExit("entry.png not found next to main.py — run render.py first")
    target_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(target_dir, exist_ok=True)
    target = os.path.join(target_dir, "entry.png")
    shutil.copyfile(source, target)
    print(f"copied {source} -> {target}")


if __name__ == "__main__":
    main()
