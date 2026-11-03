# SPDX-License-Identifier: WTFPL
"""Validate the font artifact without relying on local task files."""
import io,json,string,hashlib
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from PIL import ImageFont

ROOT=Path(__file__).resolve().parents[1];PATH=ROOT/'assets/SlopMelt-Regular.ttf'
def validate():
 f=TTFont(PATH,checkChecksums=2);cm=f.getBestCmap();gs=f.getGlyphSet()
 assert all(c in cm for c in range(32,127)), 'Missing printable ASCII character'
 assert all(cm[ord(c)]==cm[ord(c.lower())] for c in string.ascii_uppercase)
 assert f['name'].getDebugName(1)=='Slop Melt'
 assert f['name'].getDebugName(5)=='Version 0.100'
 assert 'WTFPL' in f['name'].getDebugName(13)
 for n in gs:
  b=BoundsPen(gs);gs[n].draw(b)
  if b.bounds:
   assert b.bounds[1]>=-270 and b.bounds[3]<=820,(n,b.bounds)
   assert f['hmtx'][n][0]>b.bounds[2],(n,b.bounds)
 for t in f.keys():f[t]
 data=io.BytesIO();f.save(data);assert TTFont(io.BytesIO(data.getvalue())).getBestCmap()==cm
 raster=ImageFont.truetype(str(PATH),100)
 assert all(raster.getmask(chr(c)).getbbox() for c in range(33,127))
 report={'status':'passed','glyphs':len(gs),'mapped_codepoints':len(cm),'printable_ASCII':'95/95','lowercase':'capital aliases','license':'WTFPL version 2','checks':['declared glyph bounds and positive side bearings','all font tables decompile','binary save/reopen preserves cmap','all nonspace printable ASCII characters rasterize'],'sha256':hashlib.sha256(PATH.read_bytes()).hexdigest(),'limits':['no accented letters or non-Latin scripts','no separately drawn lowercase','single display style','no physical print or commercial publishing-app testing']}
 (ROOT/'docs/validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':validate()
