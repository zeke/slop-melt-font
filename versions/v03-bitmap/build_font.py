#!/usr/bin/env python3
"""Build the v03 typeface by tracing the generated bitmap with libpotrace.

No procedural letter construction or pre-existing font is used for A-Z.
Requires Python 3.12+, numpy, scipy, Pillow, fontTools, and a Potrace shared library.
Set POTRACE_LIBRARY if the library is not found automatically; LABEL_FONT is optional.
"""
from pathlib import Path
import ctypes as C
from ctypes.util import find_library
import os
import json
import string
import zipfile
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFont
from fontTools.fontBuilder import FontBuilder
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'Slop-Melt-Bitmap-v03-A-Z.png'
OUT=ROOT/'dist'
OUT.mkdir(exist_ok=True)
(OUT/'svg-glyphs').mkdir(exist_ok=True)
(OUT/'bitmap-glyphs').mkdir(exist_ok=True)

class Point(C.Structure): _fields_=[('x',C.c_double),('y',C.c_double)]
class Curve(C.Structure): _fields_=[('n',C.c_int),('tag',C.POINTER(C.c_int)),('c',C.POINTER(Point*3))]
class PathData(C.Structure): pass
PathData._fields_=[('area',C.c_int),('sign',C.c_int),('curve',Curve),('next',C.POINTER(PathData)),('childlist',C.POINTER(PathData)),('sibling',C.POINTER(PathData)),('priv',C.c_void_p)]
class State(C.Structure): _fields_=[('status',C.c_int),('plist',C.POINTER(PathData)),('priv',C.c_void_p)]
class Bitmap(C.Structure): _fields_=[('w',C.c_int),('h',C.c_int),('dy',C.c_int),('map',C.POINTER(C.c_ulong))]
class Progress(C.Structure): _fields_=[('callback',C.c_void_p),('data',C.c_void_p),('min',C.c_double),('max',C.c_double),('epsilon',C.c_double)]
class Param(C.Structure): _fields_=[('turdsize',C.c_int),('turnpolicy',C.c_int),('alphamax',C.c_double),('opticurve',C.c_int),('opttolerance',C.c_double),('progress',Progress)]
library_path=os.environ.get('POTRACE_LIBRARY') or find_library('potrace')
if not library_path:
    raise RuntimeError('Install the Potrace shared library or set POTRACE_LIBRARY to its absolute path.')
lib=C.CDLL(library_path)
lib.potrace_param_default.restype=C.POINTER(Param)
lib.potrace_param_free.argtypes=[C.POINTER(Param)]
lib.potrace_trace.argtypes=[C.POINTER(Param),C.POINTER(Bitmap)]
lib.potrace_trace.restype=C.POINTER(State)
lib.potrace_state_free.argtypes=[C.POINTER(State)]
lib.potrace_version.restype=C.c_char_p

def trace(mask):
    h,w=mask.shape
    bits=C.sizeof(C.c_ulong)*8
    dy=(w+bits-1)//bits
    words=(C.c_ulong*(h*dy))()
    ys,xs=np.where(mask)
    for y,x in zip(ys,xs): words[int(y)*dy+int(x)//bits] |= 1 << (bits-1-int(x)%bits)
    bitmap=Bitmap(w,h,dy,words)
    params=lib.potrace_param_default()
    params.contents.turdsize=2
    params.contents.alphamax=1.0
    params.contents.opticurve=1
    params.contents.opttolerance=0.18
    state=lib.potrace_trace(params,C.byref(bitmap))
    if not state or state.contents.status!=0: raise RuntimeError('Potrace did not complete')
    pen=RecordingPen(); stats=[]
    try:
        p=state.contents.plist
        while p:
            curve=p.contents.curve
            last=curve.c[curve.n-1][2]
            pen.moveTo((last.x,last.y))
            for i in range(curve.n):
                q=curve.c[i]
                if curve.tag[i]==2:
                    pen.lineTo((q[1].x,q[1].y));pen.lineTo((q[2].x,q[2].y))
                else:
                    pen.curveTo((q[0].x,q[0].y),(q[1].x,q[1].y),(q[2].x,q[2].y))
            pen.closePath()
            stats.append({'area':p.contents.area,'sign':chr(p.contents.sign),'segments':curve.n})
            p=p.contents.next
    finally:
        lib.potrace_state_free(state);lib.potrace_param_free(params)
    return pen,stats

gray=np.asarray(Image.open(SOURCE).convert('L'))
mask=gray<128
labels,n=ndimage.label(mask)
areas=np.bincount(labels.ravel())
components=[]
for label,box in enumerate(ndimage.find_objects(labels),1):
    if areas[label]>1000:
        y,x=box
        components.append({'label':label,'x0':x.start,'x1':x.stop,'y0':y.start,'y1':y.stop,'area':int(areas[label])})
assert len(components)==26, len(components)
groups=[]
for ymin,ymax,count in [(0,300,7),(300,555,7),(555,815,7),(815,1060,5)]:
    row=sorted([a for a in components if ymin<=a['y0']<ymax],key=lambda a:a['x0'])
    assert len(row)==count
    groups.append(row)

order=['.notdef','space']+list(string.ascii_uppercase)
records={};metrics={};glyph_meta={}
nd=RecordingPen()
nd.moveTo((40,0));nd.lineTo((40,700));nd.lineTo((500,700));nd.lineTo((500,0));nd.closePath()
nd.moveTo((100,60));nd.lineTo((440,60));nd.lineTo((440,640));nd.lineTo((100,640));nd.closePath()
records['.notdef']=nd; metrics['.notdef']=(540,40)
records['space']=RecordingPen();metrics['space']=(280,0)
chars=iter(string.ascii_uppercase)
sheet_paths=[]
for row_index,row in enumerate(groups):
    row_top=min(a['y0'] for a in row)
    row_bottom=max(a['y1'] for a in row)
    scale=875/(row_bottom-row_top)
    for col_index,comp in enumerate(row):
        ch=next(chars)
        # Isolate exactly one connected black letter, preserving its white counters.
        crop=(labels[comp['y0']:comp['y1'],comp['x0']:comp['x1']]==comp['label'])
        Image.fromarray(np.where(crop,0,255).astype('uint8')).save(OUT/'bitmap-glyphs'/f'{ch}.png')
        pad=4
        raw,paths=trace(np.pad(crop,pad))
        transformed=RecordingPen()
        dx=35-pad*scale
        dy=800-(comp['y0']-row_top-pad)*scale
        raw.replay(TransformPen(transformed,(scale,0,0,-scale,dx,dy)))
        bp=BoundsPen(None);transformed.replay(bp)
        xmin,ymin,xmax,ymax=bp.bounds
        advance=round(xmax+35)
        records[ch]=transformed;metrics[ch]=(advance,round(xmin))
        svgpen=SVGPathPen(None)
        transformed.replay(TransformPen(svgpen,(1,0,0,-1,0,840)))
        d=svgpen.getCommands()
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {advance} 980"><path d="{d}" fill="currentColor"/></svg>\n'
        (OUT/'svg-glyphs'/f'{ch}.svg').write_text(svg)
        sheet_paths.append(f'<g transform="translate({col_index*1100+45},{row_index*1100+50})"><path d="{d}" fill="black"/></g>')
        glyph_meta[ch]={'source_bbox':[comp['x0'],comp['y0'],comp['x1'],comp['y1']],'source_ink_area':comp['area'],'scale':scale,'advance':advance,'bounds':bp.bounds,'contours':paths}

sheet=f'<svg xmlns="http://www.w3.org/2000/svg" width="2800" height="1600" viewBox="0 0 7800 4450"><rect width="100%" height="100%" fill="white"/>'+''.join(sheet_paths)+'</svg>\n'
(OUT/'Slop-Melt-Bitmap-v03-A-Z.svg').write_text(sheet)
cmap={32:'space',160:'space'}
for c in string.ascii_uppercase: cmap[ord(c)]=c;cmap[ord(c.lower())]=c
family='Slop Melt Bitmap v03'
names={'familyName':family,'styleName':'Regular','uniqueFontIdentifier':'SlopMeltBitmapv03-Regular-20261103','fullName':family+' Regular','psName':'SlopMeltBitmapv03-Regular','version':'Version 0.300','description':'Experimental uppercase display typeface traced from a newly generated A-Z bitmap. Lowercase keys map to uppercase forms. No digits or punctuation.','sampleText':'STOP THE SLOP'}

def build(is_ttf):
    fb=FontBuilder(1000,isTTF=is_ttf)
    fb.setupGlyphOrder(order);fb.setupCharacterMap(cmap)
    if is_ttf:
        glyphs={}
        for name in order:
            pen=TTGlyphPen(None)
            records[name].replay(Cu2QuPen(pen,0.7,reverse_direction=True))
            glyphs[name]=pen.glyph()
        fb.setupGlyf(glyphs)
    else:
        charstrings={}
        for name in order:
            pen=T2CharStringPen(metrics[name][0],None)
            records[name].replay(pen)
            charstrings[name]=pen.getCharString()
        fb.setupCFF(names['psName'],{'FullName':names['fullName'],'FamilyName':family,'Weight':'Regular','version':'0.300'},charstrings,{})
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=880,descent=-160,lineGap=0)
    fb.setupNameTable(names)
    fb.setupOS2(version=4,sTypoAscender=880,sTypoDescender=-160,sTypoLineGap=0,usWinAscent=880,usWinDescent=160,sCapHeight=800,sxHeight=800,fsType=0,fsSelection=64|128)
    fb.setupPost()
    out=OUT/('Slop-Melt-Bitmap-v03-Regular.'+('ttf' if is_ttf else 'otf'))
    fb.save(out)
    return out

ttf=build(True);otf=build(False)
font=TTFont(ttf)
font.flavor='woff';font.save(OUT/'Slop-Melt-Bitmap-v03-Regular.woff')

# Specimens are rendered using the newly compiled font, not the bitmap.
sans=os.environ.get('LABEL_FONT')
def infofont(size):
    if sans:return ImageFont.truetype(sans,size)
    return ImageFont.load_default(size=size)
def centered(draw,txt,y,size,fill,width,fontpath=ttf):
    f=ImageFont.truetype(str(fontpath),size)
    box=draw.textbbox((0,0),txt,font=f)
    x=(width-(box[2]-box[0]))/2-box[0]
    draw.text((x,y-box[1]),txt,font=f,fill=fill)
    return box[3]-box[1]

im=Image.new('RGB',(2200,1500),'#faf8ef');d=ImageDraw.Draw(im)
d.text((70,45),'SLOP MELT / BITMAP v03',font=infofont(30),fill='#473b41')
d.text((70,90),'Generated bitmap → Bézier outlines → installable font',font=infofont(23),fill='#695e62')
for y,txt in zip([170,420,670,920],['ABCDEFG','HIJKLMN','OPQRSTU','VWXYZ']):
    centered(d,txt,y,245,'#171116',2200)
d.text((70,1240),'A–Z, plus space. Lowercase keys produce these same capitals.',font=infofont(28),fill='#473b41')
d.text((70,1290),'No digits or punctuation yet. Experimental display font; spacing is a first pass.',font=infofont(28),fill='#473b41')
d.text((70,1370),'This sheet is rendered from the compiled TTF.',font=infofont(23),fill='#695e62')
im.save(OUT/'Slop-Melt-Bitmap-v03-compiled-alphabet.png')

im=Image.new('RGB',(2100,1450),'#09090b');d=ImageDraw.Draw(im)
d.text((70,45),'SLOP MELT / BITMAP v03 / FONT PROOF',font=infofont(27),fill='#b0a8b0')
for y,txt,s in [(180,'STOP',390),(580,'THE',190),(790,'SLOP',390)]:
    centered(d,txt,y,s,'#ef3d9c',2100)
d.text((70,1340),'Rounded contours and internal melt cuts traced from the generated alphabet.',font=infofont(25),fill='#b0a8b0')
im.save(OUT/'Slop-Melt-Bitmap-v03-pink-proof.png')

im=Image.new('RGB',(2400,1100),'#f9f7ed');d=ImageDraw.Draw(im)
d.text((60,40),'SLOP MELT / BITMAP v03 / TYPESETTING PROOF',font=infofont(28),fill='#55494e')
for y,txt in [(140,'THE QUICK BROWN'),(340,'FOX JUMPS OVER'),(540,'THE LAZY DOG'),(800,'Sphinx of black quartz')]:
    centered(d,txt,y,154,'#301333',2400)
im.save(OUT/'Slop-Melt-Bitmap-v03-typesetting-proof.png')

checks={}
for p in [ttf,otf,OUT/'Slop-Melt-Bitmap-v03-Regular.woff']:
    f=TTFont(p,checkChecksums=2)
    cm=f.getBestCmap()
    assert all(cm[ord(c)]==c for c in string.ascii_uppercase)
    assert all(cm[ord(c.lower())]==c for c in string.ascii_uppercase)
    assert len(f.getGlyphOrder())==28
    for c in string.ascii_uppercase:
        bounds=BoundsPen(f.getGlyphSet());f.getGlyphSet()[c].draw(bounds);assert bounds.bounds
    checks[p.name]={'glyph_count':len(f.getGlyphOrder()),'unicode_mappings':len(cm),'all_uppercase_present':True,'lowercase_aliases':True,'reload_ok':True}
for p in [ttf,otf]:
    ft=ImageFont.truetype(str(p),100)
    assert ft.getlength('ABCDEFGHIJKLMNOPQRSTUVWXYZ')>0
    checks[p.name]['freetype_load_and_render']=True

meta={'family':family,'version':'0.300','source_file':SOURCE.name,'source_dimensions':[gray.shape[1],gray.shape[0]],'threshold':128,'tracer':lib.potrace_version().decode(),'trace_parameters':{'turdsize':2,'alphamax':1.0,'opttolerance':0.18},'coverage':'26 uppercase glyphs; a-z map to capitals; space and no-break space','limitations':['No distinct lowercase','No digits, punctuation, accents, or non-Latin glyphs','First-pass spacing, no pair kerning','Experimental display typeface, not a finished production family'],'glyphs':glyph_meta,'font_checks':checks}
(OUT/'build-manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps({'output_directory':str(OUT),'font_checks':checks,'generated_glyph_count':len(glyph_meta)},indent=2))
