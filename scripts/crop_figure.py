#!/usr/bin/env python3
"""Cut figures out of a PDF as images, exactly as printed.

    python3 crop_figure.py captions paper.pdf
        List the lines that start a figure or table caption, with their page and position.

    python3 crop_figure.py page paper.pdf 5 -o page5.png [--zoom 1.5]
        Render page 5 to an image, to look at it and read off the corners of a figure.

    python3 crop_figure.py crop paper.pdf 5 80 120 530 410 -o figures/fig03.png [--zoom 3] [--from-zoom 1.5]
        Cut the rectangle (x0, y0) to (x1, y1) out of page 5 and save it at 3x zoom.

Pages are numbered from 1. Coordinates run from the top left corner of the page, x to the right and y down.
They are in PDF points by default. If you read them off an image made by the `page` command, pass that
image's zoom as --from-zoom and give the coordinates in its pixels.

Crop the figure only, without its caption: the page prints the caption as text. A zoom of 3 gives a sharp
image; set `figZoom` in the page (or `zoom` on the figure) to the zoom you used, so it is shown at its
printed size.

Needs PyMuPDF (pip install pymupdf).
"""
import argparse
import pathlib
import re
import sys

try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf
    except ImportError:
        sys.exit("This script needs PyMuPDF: pip install pymupdf")

CAPTION = re.compile(r"^\s*(Fig\.|Figure|FIGURE|TABLE|Table)\s*\.?\s*([\dIVXLC]+)")


def open_page(pdf, number):
    doc = pymupdf.open(pdf)
    if not 1 <= number <= len(doc):
        sys.exit(f"{pdf} has {len(doc)} pages; page {number} does not exist.")
    return doc[number - 1]


def save(pix, out):
    out = pathlib.Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pix.save(str(out))
    print(f"{out}: {pix.width} x {pix.height} px")


def main():
    ap = argparse.ArgumentParser(description="Cut figures out of a PDF.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("captions", help="list figure and table captions with their positions")
    a.add_argument("pdf")
    a = sub.add_parser("page", help="render one page to an image")
    a.add_argument("pdf")
    a.add_argument("page", type=int)
    a.add_argument("-o", "--out", required=True)
    a.add_argument("--zoom", type=float, default=1.5)
    a = sub.add_parser("crop", help="cut a rectangle out of a page")
    a.add_argument("pdf")
    a.add_argument("page", type=int)
    a.add_argument("box", type=float, nargs=4, metavar=("X0", "Y0", "X1", "Y1"))
    a.add_argument("-o", "--out", required=True)
    a.add_argument("--zoom", type=float, default=3)
    a.add_argument("--from-zoom", type=float, default=1, help="zoom of the image the coordinates were read from")
    args = ap.parse_args()

    if args.cmd == "captions":
        doc = pymupdf.open(args.pdf)
        for n, page in enumerate(doc, start=1):
            w, h = page.rect.width, page.rect.height
            for x0, y0, x1, y1, text, *_ in page.get_text("blocks"):
                first = text.strip().split("\n")[0]
                if CAPTION.match(first):
                    print(f"page {n} ({w:.0f} x {h:.0f} pt)  caption at x {x0:.0f}-{x1:.0f}, y {y0:.0f}-{y1:.0f}:  {first[:80]}")
        return

    page = open_page(args.pdf, args.page)
    if args.cmd == "page":
        save(page.get_pixmap(matrix=pymupdf.Matrix(args.zoom, args.zoom)), args.out)
        print(f"page size {page.rect.width:.0f} x {page.rect.height:.0f} pt, rendered at zoom {args.zoom}")
        return

    x0, y0, x1, y1 = (v / args.from_zoom for v in args.box)
    clip = pymupdf.Rect(x0, y0, x1, y1) & page.rect
    if clip.is_empty:
        sys.exit("The rectangle is empty or lies outside the page.")
    save(page.get_pixmap(matrix=pymupdf.Matrix(args.zoom, args.zoom), clip=clip), args.out)


if __name__ == "__main__":
    main()
