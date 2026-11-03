# SPDX-License-Identifier: WTFPL
"""Check supplied fonts, preservation hashes, rasterization, and README assets.

Does not regenerate fonts or overwrite any artifact. The optional --report path
writes a JSON result; otherwise results go to stdout only.
"""
from pathlib import Path
import argparse,hashlib,io,json,re,string
from urllib.parse import unquote,urlsplit
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from PIL import Image,ImageFont

ROOT=Path(__file__).resolve().parents[1]
FONTS=[('0.1','assets/SlopMelt-Regular.ttf',71,103),
 ('0.2','versions/v02-wax/assets/SlopMeltWax-Regular.ttf',71,103),
 *[('0.3','versions/v03-bitmap/dist/Slop-Melt-Bitmap-v03-Regular.'+ext,28,54) for ext in ['ttf','otf','woff']]]

def validate():
 report={'status':'passed','fonts':[],'preservation':{},'markdown_images':[]}
 for v,path,nglyph,nmap in FONTS:
  p=ROOT/path;f=TTFont(p,checkChecksums=2);cm=f.getBestCmap();gs=f.getGlyphSet()
  assert len(gs)==nglyph and len(cm)==nmap,(path,len(gs),len(cm))
  assert all(cm[ord(c)]==cm[ord(c.lower())] for c in string.ascii_uppercase),path
  if v=='0.3':
   assert set(cm)=={32,160,*map(ord,string.ascii_letters)},path
   assert 'GPOS' not in f and 'kern' not in f,path
   pairs=0
  else:
   assert all(i in cm for i in range(32,127)),path
   pairs=sum(len(s.PairValueRecord) for l in f['GPOS'].table.LookupList.Lookup for t in l.SubTable for s in getattr(t,'PairSet',[]))
   assert pairs==14,(path,pairs)
  for n in gs:
   bp=BoundsPen(gs);gs[n].draw(bp)
   if bp.bounds:
    a,b,c,d=bp.bounds
    assert b>=f['hhea'].descent-.51 and d<=f['hhea'].ascent+.51,(path,n,bp.bounds)
    assert a>=-.51 and c<=f['hmtx'][n][0]+.51,(path,n,bp.bounds)
  for table in f.keys():f[table]
  f.flavor=None;buf=io.BytesIO();f.save(buf);buf.seek(0)
  assert TTFont(buf).getBestCmap()==cm,path
  raster=ImageFont.truetype(io.BytesIO(buf.getvalue()),100)
  rendered=0
  for cp in cm:
   if cp not in (32,160):assert raster.getmask(chr(cp)).getbbox(),(path,cp);rendered+=1
  for c in string.ascii_uppercase:
   assert bytes(raster.getmask(c))==bytes(raster.getmask(c.lower())),(path,c)
  report['fonts'].append({'version':v,'path':path,'family':f['name'].getDebugName(1),'glyphs':len(gs),'unicode_mappings':len(cm),'kerning_pairs':pairs,'rendered_codepoints':rendered,'checks':['all tables decompile','cmap round trip','metrics fit','uppercase/lowercase raster aliases'],'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 for manifest_name in ['v01-preserved-files.json','imported-artifacts.json']:
  manifest=json.loads((ROOT/'docs'/manifest_name).read_text())
  for name,digest in manifest.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,('changed artifact',name)
  report['preservation'][manifest_name]=len(manifest)
 for md in [ROOT/'README.md',ROOT/'versions/v02-wax/README.md',ROOT/'versions/v03-bitmap/README.md']:
  for link in re.findall(r'!\[[^\]]*\]\(([^)]+)\)',md.read_text()):
   u=urlsplit(link);assert not u.scheme,('external README image',link)
   p=(md.parent/unquote(u.path)).resolve();assert p.is_relative_to(ROOT) and p.is_file(),link
   with Image.open(p) as im:im.verify()
   report['markdown_images'].append(str(p.relative_to(ROOT)))
 assert {'docs/type-specimen.png','docs/v02-type-specimen.png','docs/v03-type-specimen.png'}<=set(report['markdown_images'])
 # Confirm every local Markdown link resolves, including font download queries.
 for md in [ROOT/'README.md',ROOT/'versions/v02-wax/README.md',ROOT/'versions/v03-bitmap/README.md',ROOT/'THIRD_PARTY.md']:
  for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)',md.read_text()):
   u=urlsplit(link)
   if not u.scheme and u.path:assert (md.parent/unquote(u.path)).exists(),(md.name,link)
 report['limits']=['limited display-font coverage; no accents or separately drawn lowercase','0.3 has no digits, punctuation, or kerning','no physical-print or broad publishing-app test']
 return report

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path);args=parser.parse_args()
 result=json.dumps(validate(),indent=2)+'\n'
 if args.report:args.report.write_text(result)
 print(result,end='')
