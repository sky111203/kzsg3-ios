import struct
d = open(r"D:\dsh\kzsg3_port\apk_extracted\AndroidManifest.xml","rb").read()
def u16(o): return struct.unpack_from("<H", d, o)[0]
def u32(o): return struct.unpack_from("<I", d, o)[0]
# string pool at 0x8
sp = 8
hs, ssz = u16(sp+4), u32(sp+8)
scnt, soff, sutf, sstart = u32(sp+12), u32(sp+24), 0, sp+hs
strs = []
for i in range(scnt):
    off = sp + u32(sstart + i*4)
    if u16(off) == 0: strs.append("")
    else:
        l = u16(off)  # len in chars
        if sutf == 1<<8: pass
        raw = d[off+2:off+2+l*2]
        strs.append(raw.decode("utf-16le", "replace"))
# manifest element at 0x2798 start: XML start-element chunk 0x102 has attrs
def read_elems():
    o = 0x2798
    out = []
    while o < len(d)-8:
        t, hhs, hsz = struct.unpack_from("<HHI", d, o)
        if t == 0x102:
            ns, name = u32(o+20), u32(o+24)
            aline = u32(o+16)
            attrstart = o + hhs
            attrcount = u16(o+28+4)
            attrs = []
            for i in range(attrcount):
                ao = attrstart + i*20
                ans, an, av = u32(ao+4), u32(ao+8), u32(ao+16)
                atype = u16(ao+16-2)  # value type byte at +15? proper: ao+15 type, ao+16 data
                at = d[ao+15]
                ad = u32(ao+16)
                val = strs[ad] if at in (3,0x10) and ad < len(strs) else ad if at==0x10 else None
                attrs.append((strs[an] if an < len(strs) else "?", at, val))
            out.append((strs[name], attrs))
        o += hsz
    return out
elems = read_elems()
for name, attrs in elems[:4]:
    print("<"+name+">")
    for a,t,v in attrs:
        print("   ", a, "=", repr(v))
