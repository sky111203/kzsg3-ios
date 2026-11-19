import struct
p = r"D:\dsh\kzsg3_port\enginejs\cocos2d-js-v3.0-beta\frameworks\js-bindings\external\spidermonkey\prebuilt\win32\mozjs-28.dll"
d = open(p, "rb").read()
pe = struct.unpack_from("<I", d, 0x3C)[0]
opt = pe + 24
magic = struct.unpack_from("<H", d, opt)[0]
ddoff = opt + 96
exp_rva, exp_sz = struct.unpack_from("<II", d, ddoff)
nsec = struct.unpack_from("<H", d, pe+6)[0]
secoff = opt + struct.unpack_from("<H", d, pe+20)[0]
secs = []
for i in range(nsec):
    o = secoff + i*40
    vsz, va, rsz, ra = struct.unpack_from("<IIII", d, o+8)
    secs.append((va, vsz, ra))
def r2f(rva):
    for va, vsz, ra in secs:
        if va <= rva < va+max(vsz,rsz): return ra + (rva-va)
fo = r2f(exp_rva)
nnames = struct.unpack_from("<I", d, fo+24)[0]
names_rva = struct.unpack_from("<I", d, fo+32)[0]
nfo = r2f(names_rva)
names = []
for i in range(nnames):
    srva = struct.unpack_from("<I", d, nfo+i*4)[0]
    so = r2f(srva)
    e = d.index(b"\x00", so)
    names.append(d[so:e].decode())
hits = [n for n in names if "DecodeScript" in n or "NewRuntime" in n or "NewContext" in n or n.endswith("JS_Init@@YA_NXZ") or "DecompileScript" in n or "GetStringCharsZAndLength" in n or "DestroyRuntime" in n or "DestroyContext" in n or "PendingException" in n]
for h in hits: print(h)
