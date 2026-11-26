from PIL import Image, ImageFilter
for n in ("001","002"):
    a=Image.open(f"art-new/fim_bl_{n}.new.dds").convert("RGBA").getchannel("A").resize((392,440),Image.LANCZOS)
    g=a.point(lambda v:255 if v>96 else 0).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(3.5))
    g=g.point(lambda v:min(255,int(v*1.35)))
    w=Image.new("L",g.size,255); Image.merge("RGBA",(w,w,w,g)).save(f"art-new/glow_{n}.png")
