import struct
p = r"D:\dsh\kzsg3_port\enginejs\cocos2d-js-v3.0-beta\frameworks\js-bindings\external\spidermonkey\prebuilt\win32\mozjs-28.dll"
d = open(p, "rb").read()
pe = struct.unpack_from("<I", d, 0x3C)[0]
opt = pe + 24
exp_rva = struct.unpack_from("<I", d, opt+96)[0]
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
nfo = r2f(struct.unpack_from("<I", d, fo+32)[0])
names = []
for i in range(nnames):
    so = r2f(struct.unpack_from("<I", d, nfo+i*4)[0])
    names.append(d[so:d.index(b"\x00", so)].decode())
for n in names:
    if ("NewGlobalObject" in n or "JSAutoCompartment" in n or "CompartmentOptions" in n and "??0" in n
        or "InitStandardClasses" in n or "SetGCParameter" in n or "SetNativeStackQuota" in n):
        print(n)
