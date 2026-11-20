#!/usr/bin/env python3
"""news-image-20261120 v3 entrypoint.

Copies the pre-rendered broadsheet (entry.png, drawn by render_v3.py) to
/output/entry.png. Pure copy: byte-identical on every run, no network, no
fonts needed at run time. To regenerate the image from scratch, run
`python3 render_v3.py entry.png` (deterministic; same bytes every run).
"""
import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    outdir = "/output"
    if len(sys.argv) > 1:
        outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    shutil.copyfile(src, os.path.join(outdir, "entry.png"))


if __name__ == "__main__":
    main()
