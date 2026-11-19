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
        chars = d[off+4:off+4+n2]
        strs.append(chars.decode("utf-8","replace"))
    else:
        l = u16(off)
        strs.append(d[off+2:off+2+l*2].decode("utf-16le","replace"))
def read_elems():
    o = 0x2798
    out = []
    while o < len(d)-8:
        t, hhs, hsz = struct.unpack_from("<HHI", d, o)
        if t == 0x102:
            name = u32(o+24)
            attrstart = o + hhs
            attrcount = u16(o+28)
            attrs = []
            for i in range(attrcount):
                ao = attrstart + i*20
                an, at, ad = u32(ao+8), d[ao+15], u32(ao+16)
                if at == 3: val = strs[ad] if ad < len(strs) else "?"
                elif at == 0x10: val = ad
                else: val = ad
                attrs.append((strs[an] if an < len(strs) else "?", at, val))
            out.append((strs[name] if name < len(strs) else "?", attrs))
        o += hsz
    return out
elems = read_elems()
for name, attrs in elems[:3]:
    print("<"+name+">")
    for a,t,v in attrs: print("   ", a, "=", repr(v))
print("...")
# collect all activity/service/receiver + uses-sdk
for name, attrs in elems:
    if name in ("uses-sdk",):
        print(name, attrs)
