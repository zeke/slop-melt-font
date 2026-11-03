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
the generator. No third-party font outlines or font files are included. The
README images are rendered using Slop Melt itself.

The GitHub sticker is linked as a visual reference. Its photograph, graphic,
wordmark, and trademarks are not included in this repository or covered by its
WTFPL grant.
