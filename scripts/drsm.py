import struct, zlib, subprocess, sys
P="/home/leo/Documentos/Proyecto predeterminado/xc2-new-style/assets-extraidos/model/bl/"
def streams(p):
    d=open(p,"rb").read(); out=[]; i=d.find(b"xbc1")
    while i>=0:
        t,u,c=struct.unpack_from("<III",d,i+4); body=d[i+48:i+48+c]
        raw=zlib.decompress(body) if t==1 else subprocess.run(["zstd","-d","-c"],input=body,capture_output=True,check=True).stdout
        out.append((i,t,u,d[i+20:i+48].split(b"\0")[0],raw)); i=d.find(b"xbc1",i+48+c)
    return d,out
def footers(raw):
    r=[]; i=raw.find(b"LBIM")
    while i>=0:
        f=struct.unpack_from("<10I",raw,i-36); r.append((i+4,f[0],f[2],f[3],f[6],f[7])); i=raw.find(b"LBIM",i+4)
    return r
if __name__=="__main__":
    d,s=streams(P+"bl140201.wismt")
    print(len(s),"streams")
    for k,(off,t,u,name,raw) in enumerate(s):
        f=footers(raw)
        print(k,hex(off),len(raw),name,len(f),[(x[2],x[3],x[4],x[5]) for x in f[:3]])
    print("header", " ".join("%x"%v for v in struct.unpack_from("<40I",d,0)))
