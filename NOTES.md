# Project page — maintenance notes

Static project page for *MangaFlow: An End-to-End Agentic Framework for
Controllable Story to Manga Generation*. No build step, no dependencies —
plain HTML/CSS plus ~25 lines of vanilla JS for the click-to-enlarge lightbox.

Filed as `NOTES.md` rather than `README.md` on purpose, so GitHub does not
render it on the repository landing page.

```
.
├── index.html                 the whole page
├── style.css                  UTokyo palette, light + dark
├── .nojekyll                  serve files as-is, no Jekyll
├── assets/figures/*.webp      19 figures
├── assets/logos/*.png         institution and group marks
└── tools/build_figures.py     regenerates assets/figures from the sources
```

## Editing the page

`index.html` holds all the content. `style.css` holds all the styling; the
palette is a handful of CSS variables at the top of the file.

Local preview needs no server — open `index.html` in a browser and reload after
each save. To publish:

```bash
git add -A && git commit -m "what changed" && git push
```

GitHub Pages redeploys within a minute or two.

**Cache note:** browsers cache `style.css` aggressively. The stylesheet is
linked as `style.css?v=3`; bump that number whenever you change the CSS,
otherwise returning visitors keep the old file.

## Palette

Colours follow the University of Tokyo Visual Identity Guidelines
(2024-06-20 edition):

| Role | Value | Reference |
|---|---|---|
| Accent (school colour, 淡青) | `#0B8BEE` | PANTONE 2194C |
| Secondary accent | `#FFCD00` | PANTONE 116C |
| Text / surfaces | from the guideline's 15-step blue ramp | — |

The guideline caps accent colour at under 25% of a layout, which is why white
and near-black dominate and the blue is confined to section labels, buttons,
the badge and the top rule.

## Logos

| File | Placement | Notes |
|---|---|---|
| `logos/utokyo.png` | header | mark + wordmark lockup, opaque white background |
| `logos/hkust_gz.png` | header | emblem only; the wordmark beside it is set in HTML |
| `logos/nakayama_lab.png` | footer | square, carries its own background |

Header logo cards keep a white background in dark mode as well, because the
supplied files are opaque — a theme-following card would put a white block on a
dark page.

## Figures

| Section | Files |
|---|---|
| End-to-end result | `demo_p1–4` |
| Framework | `framework` |
| Layout controllability | `layout_p1–2` |
| … reference layout | `reference_layout` |
| … self-reflection | `self_reflection` |
| Long-range consistency | `memory_p1–4` |
| Renderer-agnostic | `render_flux2_p1–2`, `render_nano_p1–2` |
| Editable intermediate states | `edit_visual_reference`, `edit_lettering` |

To regenerate them, point the script at the figure sources:

```bash
PAPER_DIR=/path/to/paper EDIT_DIR=/path/to/edit-experiments \
    python3 tools/build_figures.py
```

It rasterises the PDFs with `pdftoppm`, removes the white border, downscales and
re-encodes to WebP. It intentionally does not replicate the paper's LaTeX
`trim=` crops — those exist to save column space and clipped page content when
applied to the web images.
