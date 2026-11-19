#!/usr/bin/env python3
"""Entrypoint for the news-image-20261119 entry.

Runs the one-page newspaper renderer (render.py), which writes the
1024x1024 image to /output/entry.png (and a copy next to the script
as entry.png). Deterministic: two runs are byte-identical.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import render


def main():
    render.main()


if __name__ == "__main__":
    main()
