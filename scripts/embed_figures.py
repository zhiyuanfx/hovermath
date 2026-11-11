#!/usr/bin/env python3
"""Put a hovermath page's figures inside the page, so the page is a single file.

    python3 embed_figures.py page.html              # embed, in place
    python3 embed_figures.py page.html -o out.html  # write another file
    python3 embed_figures.py page.html --clear      # remove the embedded copies again

Every figure block names its image with `src: "figures/fig01.png"`, relative to the page. This script reads
those files and stores them, base64-encoded, in the page's image slot (the script tag with the id
"hovermath-images"). The figure blocks are not changed, so the script can be run again after a figure is
replaced, and --clear returns the page to loading its figures from the folder.

Needs only the Python standard library.
"""
import argparse
import base64
import json
import pathlib
import re
import sys

SLOT = re.compile(r'<script id="hovermath-images">.*?</script>', re.S)
CONTENT = re.compile(r"/\* ==== CONTENT START ====.*?/\* ==== CONTENT END ==== \*/", re.S)
SRC = re.compile(r"""\bsrc:\s*(?:"([^"]+)"|'([^']+)')""")
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif",
        ".svg": "image/svg+xml", ".webp": "image/webp"}


def main():
    ap = argparse.ArgumentParser(description="Embed the figures of a hovermath page into the page.")
    ap.add_argument("page")
    ap.add_argument("-o", "--out", help="write to this file instead of changing the page in place")
    ap.add_argument("--clear", action="store_true", help="remove embedded figures")
    args = ap.parse_args()

    page = pathlib.Path(args.page)
    html = page.read_text(encoding="utf-8")
    if not SLOT.search(html):
        sys.exit('No image slot found: the page needs <script id="hovermath-images">const IMAGES = {};</script>.')
    block = CONTENT.search(html)
    if not block:
        sys.exit("No CONTENT START / CONTENT END markers found: is this a hovermath page?")

    images, missing = {}, []
    if not args.clear:
        srcs = sorted({a or b for a, b in SRC.findall(block.group(0))})
        for src in srcs:
            if re.match(r"(?:https?:|data:)", src):
                continue
            f = page.parent / src
            mime = MIME.get(f.suffix.lower())
            if not f.is_file() or not mime:
                missing.append(src + ("" if f.is_file() else " (file not found)") + ("" if mime else " (unsupported type)"))
                continue
            images[src] = f"data:{mime};base64," + base64.b64encode(f.read_bytes()).decode("ascii")
            print(f"embedded {src}  ({f.stat().st_size / 1024:.0f} KB)")

    slot = '<script id="hovermath-images">const IMAGES = ' + json.dumps(images, indent=0 if images else None) + ";</script>"
    html = SLOT.sub(lambda m: slot, html, count=1)
    out = pathlib.Path(args.out) if args.out else page
    out.write_text(html, encoding="utf-8")
    print(f"{out}: {len(images)} figure(s) embedded, {len(html.encode('utf-8')) / 1e6:.2f} MB")
    for m in missing:
        print("NOT embedded:", m, file=sys.stderr)
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
