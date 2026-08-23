#!/usr/bin/env python3
"""
Rebuild site/assets/figures/ from the paper's source figures.

Rasterises the paper's PDF figures, removes the uniform white border,
downscales and re-encodes to WebP.

Note on cropping: the paper applies LaTeX `trim=` to several figures so they
fit a two-column layout. This script deliberately does NOT replicate those
crops -- the web page has no column budget, and replicating them clipped page
content. Automatic white-border removal is used instead.

Requires: pdftoppm (poppler-utils), Pillow.

Source directories are read from the environment so no local path is baked in:

    PAPER_DIR=/path/to/paper  EDIT_DIR=/path/to/edit-experiments \\
        python3 site/tools/build_figures.py

PAPER_DIR must contain the paper's figure sources (mangaflow_framework_*.png
and figures/), EDIT_DIR the two intermediate-state editing demonstrations.
"""

import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.environ.get("PAPER_DIR", os.path.join(HERE, os.pardir, os.pardir, "paper"))
EDITS = os.environ.get("EDIT_DIR", os.path.join(HERE, os.pardir, os.pardir, "edit-experiments"))
OUT = os.path.join(HERE, os.pardir, "assets", "figures")
DPI = 150


def autotrim(im, pad=6, tol=8):
    """Drop a uniform near-white border, keeping `pad` px of margin."""
    grey = im.convert("L")
    diff = ImageChops.difference(grey, Image.new("L", grey.size, 255))
    bbox = diff.point(lambda v: 255 if v > tol else 0).getbbox()
    if not bbox:
        return im
    l, t, r, b = bbox
    return im.crop((max(0, l - pad), max(0, t - pad),
                    min(im.width, r + pad), min(im.height, b + pad)))


def save(src, name, maxw=1600, quality=88):
    im = Image.open(src)
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    im = autotrim(im)
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    path = os.path.join(OUT, name)
    im.save(path, "WEBP", quality=quality, method=6)
    print(f"  {os.path.getsize(path)/1024:7.0f} KB  {im.width}x{im.height}  {name}")


def rasterise(tmp, pdf, stem, first=None, last=None):
    cmd = ["pdftoppm", "-r", str(DPI), "-png"]
    if first:
        cmd += ["-f", str(first), "-l", str(last or first)]
    subprocess.run(cmd + [os.path.join(PAPER, pdf), os.path.join(tmp, stem)],
                   check=True)


def main():
    for label, d in (("PAPER_DIR", PAPER), ("EDIT_DIR", EDITS)):
        if not os.path.isdir(d):
            sys.exit(f"{label} not found: {d}\n"
                     f"Set it in the environment, e.g. {label}=/path/to/sources")
    os.makedirs(OUT, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        rasterise(tmp, "figures/text2manga_demo.pdf", "demo")
        rasterise(tmp, "figures/reference_layout/layoutref_composite.pdf", "reflayout")
        rasterise(tmp, "figures/memory/merged_stories.pdf", "memory", 1, 4)
        rasterise(tmp, "figures/render/flux2.pdf", "flux2")
        rasterise(tmp, "figures/render/nano.pdf", "nano")
        rasterise(tmp, "figures/self_reflection/self_reflect_four.pdf", "selfreflect")

        # framework diagram
        save(os.path.join(PAPER, "mangaflow_framework_v4_600dpi.png"),
             "framework.webp", maxw=2000, quality=90)
        # end-to-end text-to-manga demo
        for i in range(1, 5):
            save(f"{tmp}/demo-{i}.png", f"demo_p{i}.webp", maxw=900)
        # reference-layout-guided generation
        save(f"{tmp}/reflayout-1.png", "reference_layout.webp", maxw=1800)
        # layout-controlled generation
        save(os.path.join(PAPER, "figures/layout_control/story_18_page_001.png"),
             "layout_p1.webp", maxw=1400)
        save(os.path.join(PAPER, "figures/layout_control/story_18_page_002.png"),
             "layout_p2.webp", maxw=1400)
        # story section memory
        for i in range(1, 5):
            save(f"{tmp}/memory-{i}.png", f"memory_p{i}.webp", maxw=900)
        # renderer comparison
        for tag in ("flux2", "nano"):
            for i in (1, 2):
                save(f"{tmp}/{tag}-{i}.png", f"render_{tag}_p{i}.webp", maxw=800)
        # layout self-reflection
        save(f"{tmp}/selfreflect-1.png", "self_reflection.webp", maxw=1800)

    # intermediate-state editing demonstrations
    save(os.path.join(EDITS, "visual_reference_flux_rerender",
                      "10_visual_reference_flux_rerender_overview.png"),
         "edit_visual_reference.webp", maxw=1400)
    save(os.path.join(EDITS, "lettering",
                      "06_lettering_full_page_acceptance_view.png"),
         "edit_lettering.webp", maxw=1400)

    total = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
    print(f"\n{len(os.listdir(OUT))} files, {total/1e6:.2f} MB")


if __name__ == "__main__":
    main()
