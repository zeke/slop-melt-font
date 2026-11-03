# Slop Melt Bitmap v03

A first font made from a generated alphabet bitmap, based on the pink melting lettering experiment.

## What’s included

- `Slop-Melt-Bitmap-v03-A-Z.png`: the original generated bitmap, 1484 × 1060 pixels.
- `dist/Slop-Melt-Bitmap-v03-Regular.ttf`: installable TrueType font.
- `dist/Slop-Melt-Bitmap-v03-Regular.otf`: installable OpenType font with cubic outlines.
- `dist/Slop-Melt-Bitmap-v03-Regular.woff`: webfont.
- `dist/Slop-Melt-Bitmap-v03-A-Z.svg`: vector alphabet sheet.
- `dist/svg-glyphs/`: one SVG for each capital.
- `dist/bitmap-glyphs/`: the isolated bitmap source for each capital.
- Three proof images, all rendered with the compiled TTF.
- `build_font.py`, `generation-prompt.txt`, and build/validation records.

## Coverage

All 26 uppercase letters, space, and no-break space. Lowercase keys map to the same capitals. There are no separate lowercase shapes, numbers, punctuation, accented letters, or other scripts yet.

This is a display-font prototype. Spacing is a first pass, with no pair kerning. The Q has a small lower-right tail and can look close to O. The thin internal melt cuts work best at headline sizes.

## Use it

Install either the TTF or OTF through your font manager, then choose **Slop Melt Bitmap v03**. Installing both formats is unnecessary. This family has its own name so it can coexist with the earlier Slop Melt versions.

The font takes the text color of the app. Pink on black in the proof is a styling choice; the font itself is a single-color outline font.

## How it was made

The alphabet was generated using the original pink lettering image as a style reference. Each black glyph was isolated from the bitmap, traced with Potrace 1.16, and scaled into a common font coordinate system. The white counters and drip creases are real holes in the outlines. The TTF uses quadratic curves; the OTF retains cubic curves.

The original bitmap is preserved. Its generation record identifies the built-in image-generation tool and the earlier pink STOP THE SLOP experiment as the style reference; no specific model version was recorded. A–Z was not reconstructed from an existing font or drawn with procedural letter templates. The prompt is preserved in `generation-prompt.txt`. No third-party sticker photograph is bundled.

## Checks

- All 26 source letters were visually inspected and mapped to the matching keys.
- TTF, OTF, and WOFF reload with 28 glyphs and 54 Unicode mappings.
- All 114 letter contours are closed and fit the font metrics.
- Both desktop formats load and render in FreeType.
- Lowercase keys render identically to uppercase keys.
- The source, compiled alphabet, pink proof, and typesetting proof were visually compared.
- A normalized raster comparison of the TTF to its bitmap source gives mean intersection-over-union of 98.42%, minimum 97.45%. This checks tracing fidelity, not typographic quality.

No earlier Slop Melt files were changed. The font has not been tested in every desktop app or browser.

## Rebuild

Use Python 3.12 or newer with the pinned NumPy and SciPy versions. From the repository root, install the version-specific
Python packages:

```sh
pip install -r versions/v03-bitmap/requirements.txt
```

Install a Potrace 1.16 shared library separately. On Debian/Ubuntu the shared
library package is `libpotrace0`; on macOS it can be installed with Homebrew's
`potrace` formula. Alternatively, build Potrace with `--enable-shared`.
The script uses `ctypes.util.find_library("potrace")`. If the library is not on
its search path, point to its absolute `.so`, `.dylib`, or `.dll` location:

```sh
POTRACE_LIBRARY=/absolute/path/to/libpotrace.dylib python versions/v03-bitmap/build_font.py
python scripts/validate_versions.py
```

When discovery works, just run `python versions/v03-bitmap/build_font.py`.
The included 1484 × 1060 bitmap is the exact build input. The script thresholds
it at 128, isolates 26 connected letter components, maps four rows to A–Z,
traces them with Potrace, scales each row into font coordinates, and writes into
this version's `dist/`. FontTools converts the cubic traces into quadratic TTF
outlines (Cu2Qu tolerance 0.7); the CFF OTF retains cubic curves. WOFF packages
the TrueType font. The white creases and counters remain actual contour holes.

Proof captions use Pillow's default font unless an installed font is specified
with `LABEL_FONT=/absolute/path/to/font.ttf`. That font is used only for captions,
not for the Slop Melt glyphs. No external font file or Potrace binary is bundled.
Caption rendering may differ across environments; the supplied original proof
images are preserved here.

## License and preservation

The original bitmap, font work, prompt, and generator are included under the
repository's [WTFPL v2 policy](../../LICENSE). Potrace and Python packages retain
their own licenses; see [THIRD_PARTY.md](../../THIRD_PARTY.md). The imported TTF,
OTF, WOFF, source alphabet bitmap, traced glyphs, and proof images are unchanged.
The font name tables have no embedded license description; the repository's
LICENSE supplies the grant. The build script was adjusted only for shared-library
lookup and portable proof captions, without changing the letter tracing logic.

The fidelity statistics above are records from the initial build, not a claim
of broader typographic quality or independently recreated raster generation.
The current repository validator separately checks the supplied font files,
character coverage, metrics, lowercase aliases, and rasterization.

A separate macOS rebuild reproduced the spacing and character map. The D and H
traces showed tiny platform rounding differences, up to 2 font units in the
TrueType coordinates; the minimum rendered overlap with the supplied font was
99.98% across the tested desktop formats. See the
[rebuild report](../../docs/rebuild-validation.json). Supplied fonts remain
byte-for-byte unchanged; bit-identical cross-platform rebuilds aren't claimed.

Tracing API: https://potrace.sourceforge.net/

Font construction: https://fonttools.readthedocs.io/en/stable/fontBuilder.html
