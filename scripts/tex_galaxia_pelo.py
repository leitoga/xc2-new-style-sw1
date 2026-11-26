import json,glob,numpy as np
from PIL import Image,ImageDraw,ImageFilter
def load(i): return Image.open(glob.glob("v7/base_tex.%d.*.png"%i)[0]).convert("RGBA")
# galaxy: green source -> blue/violet ramp driven by brightness
stops=np.array([0,.12,.30,.55,.80,1.0])
cols=np.array([[8,9,34],[18,22,78],[42,42,140],[100,78,200],[150,160,245],[225,240,255]],float)
for i in (10,11,12,23):
    a=np.array(load(i)).astype(float)
    l=np.clip((a[...,:3]@[.25,.55,.20])/200,0,1)
    for c in range(3): a[...,c]=np.interp(l,stops,cols[:,c])
    Image.fromarray(a.astype(np.uint8)).save("tex-v8/%d.png"%i)
# hair: bake the second layer (orange tips) into the main hair texture by height
d=json.load(open("hairuv.json")); A=load(9); W,H=A.size
B=load(25).resize((W,H))
s=np.zeros((H,W)); n=np.zeros((H,W))
for t in d["tris"]:
    z=np.mean([v[2] for v in t]); h=(z-d["zmin"])/(d["zmax"]-d["zmin"])
    w=np.clip((0.50-h)/0.28,0,1); w=w*w*(3-2*w)
    pts=[((v[0]%1)*W,(v[1]%1)*H) for v in t]
    x0=max(int(min(p[0] for p in pts))-2,0); y0=max(int(min(p[1] for p in pts))-2,0)
    x1=min(int(max(p[0] for p in pts))+3,W); y1=min(int(max(p[1] for p in pts))+3,H)
    if x1<=x0 or y1<=y0: continue
    m=Image.new("L",(x1-x0,y1-y0),0)
    ImageDraw.Draw(m).polygon([(x-x0,y-y0) for x,y in pts],fill=1,outline=1)
    m=np.array(m); s[y0:y1,x0:x1]+=m*w; n[y0:y1,x0:x1]+=m
w=np.where(n>0,s/np.maximum(n,1),0)
w=np.array(Image.fromarray((w*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)))/255
a=np.array(A).astype(float); b=np.array(B).astype(float)
out=a.copy(); out[...,:3]=a[...,:3]*(1-w[...,None])+b[...,:3]*w[...,None]
Image.fromarray(out.astype(np.uint8)).save("tex-v8/9.png")
sheet=Image.new("RGB",(900,300))
for k,f in enumerate(["tex-v8/9.png","tex-v8/11.png"]): sheet.paste(Image.open(f).convert("RGB").resize((300,300)),(k*300,0))
sheet.paste(Image.fromarray((w*255).astype(np.uint8)).resize((300,300)),(600,0)); sheet.save("sheet8.png")
print("alpha hair",a[...,3].min(),a[...,3].max())
