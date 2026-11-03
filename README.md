# Slop Melt

A chunky, drippy display font made for the words **STOP THE SLOP**.

![STOP THE SLOP in hot pink on black](docs/stop-the-slop.png)

## Where it came from

I wanted a melting font for a STOP THE SLOP shirt. The starting point was the
pink GITHUB sticker in [this GitHub sticker pack](https://thegithubshop.com/collections/stickers/products/1547508-00-logo-stickers-pack-of-12).
We couldn't identify the original typeface, so I asked Codex to make a new one.

This is the first version we came up with: uneven edges, chunky letters, and
little drips hanging off the bottom. All of its letter outlines were constructed
from scratch in Python. The sticker supplied the visual inspiration; its artwork
wasn't traced or included here. Its original font and designer remain unidentified.

This repository preserves the 0.1 letterforms. The later waxier experiment is
being kept separately.

## Try it

[Download SlopMelt-Regular.ttf](assets/SlopMelt-Regular.ttf?raw=true) and install it
like any other font. It has one style, Regular. Typing lowercase gives you capitals.

For a ready-made graphic, there's a [black SVG](assets/stop-the-slop-black.svg)
with a transparent background. You can recolor the paths in a vector editor.

## Type specimen

![Slop Melt alphabet, numerals, and punctuation](docs/type-specimen.png)

There are 71 glyphs and 103 mapped codepoints: A–Z, 0–9, all 95 printable ASCII
characters, and a few punctuation aliases. Lowercase letters share the capital
outlines. Curly quotes share the straight-quote designs; en and em dashes share
the hyphen. The font has 15 kerning pairs.

Accents, non-Latin scripts, separately drawn lowercase, and additional weights
aren't included. It's an early display font. The skinny drip tips deserve a look
at the final size before printing.

## How it was made

The actual recipe is in [source/build_font.py](source/build_font.py):

1. Define each letter's skeleton with line segments and cubic Bézier curves.
   The curves are sampled into points.
2. Use Shapely to thicken those paths into rounded strokes and merge them into
   a solid letter body.
3. Add tapered drip polygons where the letter reaches the baseline. Open the
   A's counter explicitly so it stays readable.
4. Apply small sine-wave displacements to the contours, then simplify them.
   Each character has a fixed phase, so its rough edges are repeatable.
5. Orient the outer contours and holes, then turn the contour points into
   quadratic outlines with FontTools pens. Consecutive midpoint endpoints soften
   the corners.
6. Add advance widths, side bearings, the character map, vertical metrics, and
   naming tables with FontBuilder. Compile the kerning feature into GPOS.
7. Save the TrueType font, the editable UFO with ufoLib2, a TTX table dump, and
   SVG/JSON outlines for artwork and previews.

Codex wrote and ran the generator. No image-generation model, traced raster,
or third-party font outlines were used to draw these glyphs. Paper was used to
review and arrange the resulting SVG lettering in the three shirt colorways.

For this public copy, the embedded license description was changed to WTFPL v2.
The glyph outlines, spacing, metrics, and kerning match the original 0.1 build.
The original working files remain preserved separately.

## Edit or rebuild

The [UFO source](source/SlopMelt-Regular.ufo) opens in a UFO-compatible font editor.
You can also edit the Python skeletons and drip construction directly.

Use Python 3.11 or newer:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python source/build_font.py
python source/render_specimens.py
python source/validate_font.py
```

The build writes the TTF, TTX, JSON outlines, and individual SVGs under `assets/`,
and the UFO under `source/`. The specimen script renders the two README images
using Slop Melt itself, with no extra font downloads.

Validation checks the character map, glyph bounds, spacing, table round trip,
and rasterization of every printable ASCII character. HarfBuzz also shaped
STOP THE SLOP without missing glyphs in the initial review. Fontconfig's broader
English-language coverage check reports 20 missing characters, consistent with
the limited character set above. No physical print or commercial publishing-app
testing has been done.

## License

The original Slop Melt font, code, and artwork are released under
[WTFPL version 2](LICENSE). Copyright 2026 Zeke Sikelianos.

The standard license text was retrieved from [wtfpl.net](https://www.wtfpl.net/txt/copying/).
The copyright line in that document credits its author, Sam Hocevar.

Build dependencies keep their own licenses; see [THIRD_PARTY.md](THIRD_PARTY.md).
No third-party package code, reference sticker artwork, or third-party font files
are bundled. This project grants no rights to GitHub's artwork or trademarks.
