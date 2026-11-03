"""Original skeletons and melting outlines. No third-party font outlines used."""
from pathlib import Path
import json, math, random, string
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union, transform
from shapely.geometry.polygon import orient
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
import ufoLib2

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'; OUT.mkdir(exist_ok=True)
def curve(p):
    a,b,c,d=p
    return [tuple((1-t)**3*a[j]+3*(1-t)**2*t*b[j]+3*(1-t)*t*t*c[j]+t**3*d[j] for j in (0,1)) for t in [i/32 for i in range(33)]]
def C(*p):return curve(p)
S=C((460,570),(100,800),(0,430),(300,365))+C((300,365),(650,260),(430,-90),(100,105))[1:]
O=C((300,620),(10,630),(10,80),(280,78))+C((280,78),(600,45),(590,650),(300,620))[1:]
P=[(120,75),(120,615),(300,620)]+C((300,620),(600,635),(600,330),(310,330))[1:]+[(120,330)]
SKELETON={
'A':[[(90,80),(285,620),(485,80)],[(170,290),(410,300)]],
'B':[[(120,80),(120,620),(290,620)]+C((290,620),(600,640),(570,370),(290,365))[1:]+C((290,365),(640,390),(590,60),(310,80))[1:]+[(120,80)]],
'C':[C((480,565),(40,830),(-10,-100),(480,130))],
'D':[[(120,80),(120,620),(260,620)]+C((260,620),(660,650),(650,45),(260,80))[1:]+[(120,80)]],
'E':[[(465,620),(120,620),(120,80),(475,80)],[(125,360),(410,365)]],
'F':[[(120,80),(120,620),(470,620)],[(120,360),(400,365)]],
'G':[C((480,560),(40,830),(-10,-100),(475,130))+[(480,330),(320,330)]],
'H':[[(120,80),(120,620)],[(475,80),(475,620)],[(120,350),(475,370)]],
'I':[[(120,620),(120,80)]],
'J':[[(450,620),(450,220)]+C((450,220),(450,-25),(90,15),(100,215))[1:]],
'K':[[(120,80),(120,620)],[(480,620),(130,340),(500,80)]],
'L':[[(120,620),(120,80),(465,80)]],
'M':[[(110,80),(110,620),(330,320),(550,620),(550,80)]],
'N':[[(120,80),(120,620),(480,80),(480,620)]],
'O':[O], 'P':[P],
'Q':[O,[(365,220),(535,30)]],
'R':[P,[(300,330),(500,80)]], 'S':[S],
'T':[[(80,620),(510,620)],[(300,620),(300,80)]],
'U':[[(120,620),(120,250)]+C((120,250),(90,-20),(510,0),(490,250))[1:]+[(490,620)]],
'V':[[(90,620),(290,80),(495,620)]],
'W':[[(100,620),(210,80),(370,390),(520,80),(635,620)]],
'X':[[(100,620),(500,80)],[(480,620),(110,80)]],
'Y':[[(90,620),(300,355),(505,620)],[(300,355),(300,80)]],
'Z':[[(100,620),(490,620),(100,80),(505,80)]],
'0':[O], '1':[[(100,490),(270,620),(270,80)],[(120,80),(420,80)]],
'2':[C((100,530),(220,790),(680,560),(385,340))+[(100,80),(500,80)]],
'3':[C((110,580),(520,800),(650,350),(295,370))+C((295,370),(680,410),(530,-100),(100,120))[1:]],
'4':[[(405,80),(405,620),(90,245),(515,245)]],
'5':[[(480,620),(125,620),(110,365)]+C((110,365),(650,540),(650,-100),(100,115))[1:]],
'6':[C((450,580),(150,800),(-70,60),(270,80))+C((270,80),(650,20),(610,530),(145,330))[1:]],
'7':[[(90,620),(510,620),(235,80)]],
'8':[C((300,365),(-100,330),(50,800),(300,620))+C((300,620),(630,750),(660,350),(300,365))[1:]+C((300,365),(-90,380),(-10,-75),(300,80))[1:]+C((300,80),(650,0),(680,420),(300,365))[1:]],
'9':[C((150,120),(450,-100),(670,640),(330,620))+C((330,620),(-50,680),(-10,170),(455,370))[1:]],
}

def drip(x,y,length,width=34):
    p=[(x-width*1.9,y+65)]
    p+=C((x-width*1.9,y+65),(x-width*.8,y+25),(x-width*.7,y-length+25),(x-width*.75,y-length))[1:]
    p+=C((x-width*.75,y-length),(x-width*.3,y-length-48),(x+width*.9,y-length-35),(x+width*.65,y-length+5))[1:]
    p+=C((x+width*.65,y-length+5),(x+width*.6,y+15),(x+width*1.4,y+35),(x+width*1.9,y+65))[1:]
    return Polygon(p)

def wax_cut(x,y,length,width=16,bend=0):
    """A sinuous negative fold. Broad at its mouth, pinched at its molten foot."""
    left=C((x-width,y),(x-width*.55,y-length*.15),(x-width*.22+bend,y-length*.48),(x-width*.76+bend,y-length*.77))
    foot=C(left[-1],(x-width*1.16+bend,y-length-27),(x+width*.94+bend,y-length-27),(x+width*.68+bend,y-length*.80))
    right=C(foot[-1],(x+width*.18+bend,y-length*.48),(x+width*.50,y-length*.12),(x+width,y))
    return Polygon(left+foot[1:]+right[1:]).buffer(0)

# Face folds are largely anchored to a contour or counter, not sprinkled as dots.
SEAMS={
'S':[(242,745,206,19,15),(413,360,167,16,-33),(152,176,140,13,28)],
'T':[(163,760,192,18,14),(413,757,210,20,-23),(296,454,219,12,18)],
'O':[(195,750,184,21,-12),(487,539,251,19,-35),(187,204,135,13,24)],
'P':[(135,760,270,21,-5),(396,621,153,18,-23),(130,261,192,12,16)],
'H':[(119,760,271,20,13),(476,760,250,22,-14),(305,415,120,17,-25)],
'E':[(249,760,187,22,-13),(116,514,224,13,17),(300,144,128,18,-18)],
'L':[(127,760,275,20,-11),(146,275,180,12,22),(340,146,129,20,12)],
'G':[(208,750,193,19,21),(119,467,206,13,-15),(405,369,110,16,-22)],
'I':[(119,760,262,20,13),(116,348,202,12,-18)],
}

def make(ch,paths):
    seed=ord(ch)
    # A thicker body gives the negative spaces room to flow through the letter face.
    geom=unary_union([LineString(p).buffer(103,quad_segs=16,join_style='round') for p in paths])
    # Small blunt lobes replace the hanging filaments of 0.1.
    lo,bot,hi,top=geom.bounds
    for f in (.27,.73):
        x=lo+(hi-lo)*f
        ys=[yy for yy in range(-18,145,4) if geom.contains(Point(x,yy))]
        if ys:
            y=min(ys)+14;geom=geom.union(Point(x,y-13-(seed%4)*5).buffer(43+(seed%3)*5,quad_segs=14))
    if ch=='A':geom=geom.difference(Polygon([(245,337),(323,337),(284,491)]).buffer(12))
    if ch=='4':geom=geom.difference(Polygon([(246,350),(354,350),(354,490)]).buffer(8))
    # Melt the counter roofs: thick wax tongues intrude into O/P/B/D/R counters.
    for poly in ([geom] if geom.geom_type=='Polygon' else geom.geoms):
        for ring in poly.interiors:
            hole=Polygon(ring);a,b,c,d=hole.bounds
            if d-b>80 and c-a>60:
                x=a+(c-a)*(.42 if seed%2 else .62)
                tongue=Point(x+10,d-57).buffer(27,quad_segs=12).union(LineString([(x,d+18),(x+10,d-57)]).buffer(24))
                geom=geom.union(tongue.intersection(hole.buffer(8)))
    if ch=='G':geom=geom.difference(box(440,383,700,505).buffer(20))
    phase=(seed%11)*.7
    def warp(x,y,z=None):
        return (x+19*math.sin(y/58+phase)+10*math.sin(y/23+phase),y+20*math.sin(x/53+phase)+11*math.sin(x/23+phase))
    geom=transform(warp,geom.segmentize(8)).buffer(11,quad_segs=12).buffer(-11,quad_segs=12).simplify(1.1,preserve_topology=True)
    seams=SEAMS.get(ch)
    if seams is None:
        # Place 1–3 vertical creases inside the original strokes, never scatter dots.
        seams=[]
        for f,y in [(0.28,540),(0.73,425),(0.45,180)]:
            x=lo+(hi-lo)*f
            if geom.contains(Point(x,y)) and geom.contains(Point(x,y-75)):
                seams.append((x,y,110,15,6 if seed%2 else -6))
    for x,y,length,width,bend in seams:
        cut=transform(warp,wax_cut(x,y,length,width*1.25,bend))
        geom=geom.difference(cut)
    geom=geom.buffer(-3,quad_segs=8).buffer(3,quad_segs=8)
    # Remove accidental tiny islands; retain deliberate counters and connected wax forms.
    if geom.geom_type=='MultiPolygon':geom=unary_union([p for p in geom.geoms if p.area>400])
    x0=geom.bounds[0];geom=transform(lambda x,y,z=None:(x-x0+44,y),geom)
    return geom,round(geom.bounds[2]+44)

GEOMS={}; WIDTH={}; CMAP={}; GLYPHS={}; UFO=ufoLib2.Font()
UFO.info.familyName='Slop Melt Wax';UFO.info.styleName='Regular';UFO.info.unitsPerEm=1000
UFO.info.ascender=820;UFO.info.descender=-270;UFO.info.capHeight=700
def draw(geom,pen):
    polys=list(geom.geoms) if geom.geom_type=='MultiPolygon' else [geom]
    for poly in polys:
        poly=orient(poly,sign=-1)
        for ring in [poly.exterior]+list(poly.interiors):
            pts=list(ring.coords)[:-1]
            midpoint=lambda a,b:tuple(round((a[j]+b[j])/2) for j in (0,1))
            pen.moveTo(midpoint(pts[-1],pts[0]))
            for i,p in enumerate(pts):pen.qCurveTo(tuple(round(v) for v in p),midpoint(p,pts[(i+1)%len(pts)]))
            pen.closePath()
def add(name,geom,width,unicodes=[]):
    pen=TTGlyphPen(None)
    g=UFO.newGlyph(name);g.width=width;g.unicodes=unicodes
    if geom and not geom.is_empty:draw(geom,pen);draw(geom,g.getPen())
    GLYPHS[name]=pen.glyph();WIDTH[name]=width;GEOMS[name]=geom
    for c in unicodes:CMAP[c]=name
add('.notdef',box(45,0,495,700).difference(box(125,80,415,620)),540)
add('space',None,280,[32,160])
for ch,paths in SKELETON.items():
    geom,width=make(ch,paths)
    add(ch,geom,width,[ord(ch)]+([ord(ch.lower())] if ch.isalpha() else []))

def stroke(*p,r=52):return LineString(p).buffer(r,quad_segs=8)
dot=Point(110,55).buffer(57,quad_segs=10)
PUNCT={
'.':dot,',':unary_union([dot,stroke((115,65),(70,-80),r=35)]),
':':unary_union([dot,Point(110,395).buffer(57)]),';':unary_union([dot,Point(110,395).buffer(57),stroke((110,30),(65,-80),r=32)]),
'!':unary_union([dot,stroke((110,240),(120,635),r=65)]),
'?':unary_union([dot,LineString(C((70,550),(210,790),(480,530),(260,350))+[(200,220)]).buffer(62)]),
"'":stroke((100,650),(80,495),r=40),'"':unary_union([stroke((100,650),(80,495),r=35),stroke((250,650),(230,495),r=35)]),
'-':stroke((80,300),(320,310),r=50),'_':stroke((70,-100),(460,-100),r=45),
'+':unary_union([stroke((80,320),(440,320)),stroke((260,140),(260,500))]),
'=':unary_union([stroke((80,230),(440,230)),stroke((80,420),(440,420))]),
'/':stroke((70,20),(390,650),r=48),'\\':stroke((70,650),(390,20),r=48),
'(':LineString(C((240,700),(-10,570),(-10,50),(240,-70))).buffer(48),
')':LineString(C((80,700),(330,570),(330,50),(80,-70))).buffer(48),
'[':stroke((250,700),(90,700),(90,-60),(250,-60),r=45),']':stroke((90,700),(250,700),(250,-60),(90,-60),r=45),
'<':stroke((350,600),(90,330),(350,60),r=45),'>':stroke((90,600),(350,330),(90,60),r=45),
'*':unary_union([stroke((100,450),(360,620),r=35),stroke((100,620),(360,450),r=35),stroke((230,370),(230,690),r=35)]),
'#':unary_union([stroke((160,50),(250,650),r=40),stroke((370,50),(460,650),r=40),stroke((85,240),(535,240),r=40),stroke((115,450),(565,450),r=40)]),
'|':stroke((100,-80),(100,710),r=43),'~':LineString(C((70,300),(210,500),(330,130),(470,350))).buffer(40),
'^':stroke((80,450),(240,650),(400,450),r=40),'`':stroke((80,700),(150,590),r=35),
'{':stroke((270,700),(150,640),(150,400),(70,330),(150,270),(150,30),(270,-40),r=40),
'}':stroke((70,700),(190,640),(190,400),(270,330),(190,270),(190,30),(70,-40),r=40),
}
PUNCT['&']=unary_union([LineString(C((430,500),(200,800),(-30,390),(300,280))+C((300,280),(650,100),(130,-130),(90,180))[1:]+[(480,520)]).buffer(65),stroke((190,360),(520,80),r=62)])
PUNCT['%']=unary_union([stroke((90,40),(470,650),r=40),Point(130,550).buffer(90).difference(Point(130,550).buffer(32)),Point(430,140).buffer(90).difference(Point(430,140).buffer(32))])
PUNCT['$']=unary_union([LineString(S).buffer(65),stroke((275,-60),(300,730),r=32)])
PUNCT['@']=unary_union([LineString(O).buffer(55),Point(300,330).buffer(105).difference(Point(300,330).buffer(35)),stroke((410,460),(410,250),(495,250),r=36)])
for ch,geom in PUNCT.items():
    x0=geom.bounds[0];geom=transform(lambda x,y,z=None:(x-x0+42,y),geom)
    add('uni%04X'%ord(ch),geom,round(geom.bounds[2]+42),[ord(ch)])
# Unicode punctuation aliases are intentionally documented, rather than implied language coverage.
for cp,ch in {0x2018:"'",0x2019:"'",0x201c:'"',0x201d:'"',0x2013:'-',0x2014:'-',0x2026:'.'}.items():
    if cp==0x2026:
        geom=unary_union([transform(lambda x,y,z=None:(x+i*190,y),dot) for i in range(3)])
        add('ellipsis',geom,570,[cp])
    else:
        CMAP[cp]=CMAP[ord(ch)]
        UFO[CMAP[cp]].unicodes.append(cp)

fb=FontBuilder(1000,isTTF=True);fb.setupGlyphOrder(list(GLYPHS));fb.setupCharacterMap(CMAP)
fb.setupGlyf(GLYPHS);fb.setupHorizontalMetrics({n:(WIDTH[n],int(GEOMS[n].bounds[0]) if GEOMS[n] else 0) for n in GLYPHS})
fb.setupHorizontalHeader(ascent=820,descent=-270,lineGap=80)
fb.setupNameTable({'familyName':'Slop Melt Wax','styleName':'Regular','uniqueFontIdentifier':'Zeke-SlopMeltWax-Regular-0.2','fullName':'Slop Melt Wax Regular','psName':'SlopMeltWax-Regular','version':'Version 0.200','copyright':'Original design created for Zeke, 2026.','licenseDescription':'Original font software supplied under MIT License. See LICENSE.txt. No rights in GitHub artwork or marks are granted.'})
fb.setupOS2(sTypoAscender=820,sTypoDescender=-270,sTypoLineGap=80,usWinAscent=820,usWinDescent=270,sxHeight=700,sCapHeight=700,fsSelection=0x40)
fb.setupPost();fb.setupMaxp()
kern={('T','O'):-35,('T','S'):-20,('T','A'):-60,('T','H'):-12,('L','O'):-25,('L','T'):-45,('S','T'):-20,('P','T'):-20,('A','V'):-50,('V','A'):-50,('W','A'):-30,('Y','O'):-40,('O','P'):-12,('S','L'):-8}
fea='languagesystem DFLT dflt; feature kern {\n'+''.join(f'pos {a} {b} {v};\n' for (a,b),v in kern.items())+'} kern;'
addOpenTypeFeaturesFromString(fb.font,fea);fb.save(OUT/'SlopMeltWax-Regular.ttf')
UFO.kerning.update(kern);UFO.features.text=fea;UFO.save(ROOT/'source'/'SlopMeltWax-Regular.ufo',overwrite=True)
font=TTFont(OUT/'SlopMeltWax-Regular.ttf');font.saveXML(OUT/'SlopMeltWax-Regular.ttx')
gs=font.getGlyphSet(); paths={}
for name in gs:
    pen=SVGPathPen(gs);gs[name].draw(pen);paths[name]=pen.getCommands()
json.dump({'paths':paths,'widths':WIDTH,'cmap':{chr(k):v for k,v in CMAP.items()},'kerning':{a+':'+b:v for (a,b),v in kern.items()}},open(OUT/'glyphs.json','w'),indent=2)
for ch in 'STOPHEL':
    n=CMAP[ord(ch)]
    (OUT/f'glyph-{ch}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -820 {WIDTH[n]} 1090"><path d="{paths[n]}" transform="scale(1,-1)"/></svg>')
print('Built',len(GLYPHS),'glyphs,',len(CMAP),'mapped codepoints')
