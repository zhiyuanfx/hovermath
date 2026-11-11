#!/usr/bin/env python3
"""Make a copy of a hovermath page that opens without an internet connection.

    python3 make_offline.py page.html               # writes page.offline.html
    python3 make_offline.py page.html -o out.html

A hovermath page normally loads KaTeX (the math renderer: one script, one stylesheet and its fonts) from
cdn.jsdelivr.net when it opens. This script puts KaTeX inside the page instead, which adds about 0.65 MB.

KaTeX is taken from the first of these that has it:
  1. assets/katex/ in the hovermath folder (katex.min.js, katex.min.css, fonts/*.woff2), if you keep a copy there;
  2. the cache folder ~/.cache/hovermath/katex-<version>/;
  3. cdn.jsdelivr.net, downloaded once into that cache folder (this step needs internet).

Needs only the Python standard library.
"""
import argparse
import base64
import pathlib
import re
import sys
import urllib.request

VERSION = "0.16.11"
CDN = f"https://cdn.jsdelivr.net/npm/katex@{VERSION}/dist/"
CSS_LINK = re.compile(r'<link rel="stylesheet" href="https://cdn\.jsdelivr\.net/npm/katex@[\d.]+/dist/katex\.min\.css">')
JS_TAG = re.compile(r'<script src="https://cdn\.jsdelivr\.net/npm/katex@[\d.]+/dist/katex\.min\.js"></script>')
FONT = re.compile(r"fonts/[\w-]+\.woff2")
# One @font-face source list: the woff2 file first, then older formats, which the offline copy drops.
FONT_SRC = re.compile(r'src:url\((fonts/[\w-]+\.woff2)\) format\("woff2"\)[^;}]*')


def fetch(name, folder):
    target = folder / name
    if not target.is_file():
        target.parent.mkdir(parents=True, exist_ok=True)
        print("downloading", CDN + name)
        with urllib.request.urlopen(CDN + name, timeout=60) as r:
            target.write_bytes(r.read())
    return target


def katex_folder():
    local = pathlib.Path(__file__).resolve().parent.parent / "assets" / "katex"
    if (local / "katex.min.js").is_file() and (local / "katex.min.css").is_file():
        return local, False
    return pathlib.Path.home() / ".cache" / "hovermath" / f"katex-{VERSION}", True


def main():
    ap = argparse.ArgumentParser(description="Make a hovermath page that works offline.")
    ap.add_argument("page")
    ap.add_argument("-o", "--out", help="output file (default: <page>.offline.html)")
    args = ap.parse_args()

    page = pathlib.Path(args.page)
    html = page.read_text(encoding="utf-8")
    if not CSS_LINK.search(html) or not JS_TAG.search(html):
        sys.exit("The KaTeX <link> and <script> tags were not found: the page may already be offline.")

    folder, may_download = katex_folder()

    def get(name):
        if may_download:
            return fetch(name, folder)
        f = folder / name
        if not f.is_file():
            sys.exit(f"{f} is missing from the local KaTeX copy.")
        return f

    css = get("katex.min.css").read_text(encoding="utf-8")
    fonts = sorted(set(FONT.findall(css)))

    def font_src(m):
        data = base64.b64encode(get(m.group(1)).read_bytes()).decode("ascii")
        return f'src:url(data:font/woff2;base64,{data}) format("woff2")'

    css, n = FONT_SRC.subn(font_src, css)
    if n != len(fonts):
        print(f"warning: {len(fonts)} fonts named in the stylesheet, {n} embedded", file=sys.stderr)
    js = get("katex.min.js").read_text(encoding="utf-8").replace("</script", "<\\/script")

    html = CSS_LINK.sub(lambda m: f'<style id="katex-css">{css}</style>', html, count=1)
    html = JS_TAG.sub(lambda m: f'<script id="katex-js">{js}</script>', html, count=1)
    out = pathlib.Path(args.out) if args.out else page.with_suffix(".offline.html")
    out.write_text(html, encoding="utf-8")
    print(f"{out}: KaTeX {VERSION} and {n} fonts embedded, {len(html.encode('utf-8')) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
