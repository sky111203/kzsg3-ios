import struct
d = open(r"D:\dsh\kzsg3_port\apk_extracted\AndroidManifest.xml","rb").read()
def u16(o): return struct.unpack_from("<H", d, o)[0]
def u32(o): return struct.unpack_from("<I", d, o)[0]
sp = 8
hs = u16(sp+4); scnt = u32(sp+12); flags = u32(sp+16); sstart = u32(sp+20)
is_utf8 = bool(flags & 0x100)
strs = []
for i in range(scnt):
    off = sp + sstart + u32(sp + hs + i*4)
    if is_utf8:
        n = u16(off); n2 = u16(off+2)
        strs.append(d[off+4:off+4+n2].decode("utf-8","replace"))
    else:
        l = u16(off)
        strs.append(d[off+2:off+2+l*2].decode("utf-16le","replace"))
o = 0x2798
elems = []
while o < len(d)-8:
    t, hhs, hsz = struct.unpack_from("<HHI", d, o)
    if t == 0x102:
        name = u32(o+20)
        astart = u16(o+24); acount = u16(o+28)
        attrs = []
        for i in range(acount):
            ao = o + astart + i*20
            an, at, ad = u32(ao+8), d[ao+15], u32(ao+16)
            val = strs[ad] if (at == 3 and ad < len(strs)) else ad
            attrs.append((strs[an] if an < len(strs) else "?", val))
        elems.append((strs[name] if name < len(strs) else "?", attrs))
    o += hsz
for name, attrs in elems[:2]:
    print("<"+name+">"); 
    for a,v in attrs: print("   ", a, "=", repr(v))
for name, attrs in elems:
    if name == "uses-sdk": print("uses-sdk:", attrs)
    if name == "application":
        dd = dict(attrs)
        print("application label:", dd.get("label"), "icon:", dd.get("icon"))
