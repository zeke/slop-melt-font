# Build tools and their licenses

WTFPL v2 applies to the original Slop Melt font, generator, and artwork in this
repository. It does not relicense the tools used to produce them.

| Tool | Pinned version | Upstream license |
| --- | --- | --- |
| [FontTools](https://github.com/fonttools/fonttools/blob/main/LICENSE) | 4.68.0 | MIT |
| [Shapely](https://github.com/shapely/shapely/blob/main/LICENSE.txt) | 2.2.0 | BSD-3-Clause |
| [ufoLib2](https://github.com/fonttools/ufoLib2/blob/main/LICENSE) | 0.19.1 | Apache-2.0 |
| [Pillow](https://github.com/python-pillow/Pillow/blob/main/LICENSE) | 13.0.0 | MIT-CMU |

These identifiers were checked against the installed distributions' metadata
and license files when preparing the public repository on 2026-11-03.

Shapely uses GEOS, which is licensed under LGPL-2.1-or-later. NumPy, a Shapely
dependency, reports BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 in the
installed 2.5.4 distribution. attrs, used by ufoLib2, is MIT licensed. FontTools
and Pillow distributions also carry notices for bundled components. Those
licenses and notices remain with the packages installed by pip.

This repository distributes the generator and its outputs, without vendoring
the dependencies or their binary libraries. No library source was copied into
the generator. No third-party font outlines or font files are included.
The original 0.1 README images are rendered using Slop Melt itself. The imported
0.2 and 0.3 proofs use their corresponding Slop Melt fonts for the glyphs; their
caption text may use installed system fonts. No such font files are bundled.

The GitHub sticker is linked as a visual reference. Its photograph, graphic,
wordmark, and trademarks are not included in this repository or covered by its
WTFPL grant.

## Bitmap 0.3 tools

The bitmap builder additionally uses [SciPy](https://github.com/scipy/scipy/blob/main/LICENSE.txt)
(BSD-3-Clause), NumPy (licenses noted above), and [Potrace 1.16](https://potrace.sourceforge.net/)
(GPL-2.0-or-later). Its separate Python requirements record the tested versions.
Potrace is installed externally and loaded through its public tracing API;
its code and shared libraries are not redistributed or relicensed here. Its
license applies to that dependency, not a new WTFPL grant over the dependency.
Pillow's default proof-caption font or an explicitly selected installed font
can be used for rebuilds; no third-party font binary is included.

The original 0.2 MIT notice is retained in versions/v02-wax/LICENSE.txt because
the preserved font metadata references that initial grant. The original font
work is additionally offered under the repository's WTFPL policy. The imported
0.3 name tables have no embedded license description; their license is supplied
by the repository. No supplied font binary was rewritten for this update.
