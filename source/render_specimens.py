# SPDX-License-Identifier: WTFPL
"""Render original Slop Melt artwork with its own font, without external assets."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
FONT=ROOT/'assets/SlopMelt-Regular.ttf';DOCS=ROOT/'docs';DOCS.mkdir(exist_ok=True)
def fit(text,size,maxwidth):
 f=ImageFont.truetype(str(FONT),size)
 if f.getlength(text)>maxwidth:f=ImageFont.truetype(str(FONT),int(size*maxwidth/f.getlength(text)))
 return f
def render():
 im=Image.new('RGB',(1800,1600),'black');d=ImageDraw.Draw(im)
 for text,y,size in [('STOP',100,550),('THE',620,280),('SLOP',1000,550)]:
  d.text((900,y),text,font=fit(text,size,1500),fill='#FF65B8',anchor='mt',features=['kern'])
 im.save(DOCS/'stop-the-slop.png')
 im=Image.new('RGB',(2400,1750),'white');d=ImageDraw.Draw(im)
 d.text((100,70),'SLOP MELT',font=fit('SLOP MELT',150,2200),fill='#492047',anchor='lt')
 for text,y in [('ABCDEFGHI',340),('JKLMNOPQR',630),('STUVWXYZ',920),('0123456789',1210)]:
  d.text((1200,y),text,font=fit(text,280,2200),fill='black',anchor='mt',features=['kern'])
 text='! ? & @ # % . , : ;'
 d.text((1200,1510),text,font=fit(text,150,2200),fill='#492047',anchor='mt')
 im.save(DOCS/'type-specimen.png')
if __name__=='__main__':render()
