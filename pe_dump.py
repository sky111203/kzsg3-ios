import struct
p = r"D:\dsh\kzsg3_port\enginejs\cocos2d-js-v3.0-beta\frameworks\js-bindings\external\spidermonkey\prebuilt\win32\mozjs-28.dll"
d = open(p, "rb").read()
print("size", len(d), "MZ:", d[:2])
pe = struct.unpack_from("<I", d, 0x3C)[0]
print("PE sig:", d[pe:pe+4])
machine = struct.unpack_from("<H", d, pe+4)[0]
print("machine:", hex(machine))
# data directories
opt = pe + 24
magic = struct.unpack_from("<H", d, opt)[0]
print("opt magic:", hex(magic))
ddoff = opt + (96 if magic == 0x10b else 112)
exp_rva, exp_sz = struct.unpack_from("<II", d, ddoff)
print("export dir rva", hex(exp_rva), "size", exp_sz)
# sections for rva->file mapping
nsec = struct.unpack_from("<H", d, pe+6)[0]
secoff = opt + struct.unpack_from("<H", d, pe+20)[0]
secs = []
for i in range(nsec):
    o = secoff + i*40
    nm = d[o:o+8].rstrip(b"\0").decode()
    vsz, va, rsz, ra = struct.unpack_from("<IIII", d, o+8)
    secs.append((nm, va, vsz, ra, rsz))
    print(f"sec {nm} va={va:#x} vsz={vsz:#x} ra={ra:#x} rsz={rsz:#x}")
def r2f(rva):
    for nm, va, vsz, ra, rsz in secs:
        if va <= rva < va+max(vsz,rsz):
            return ra + (rva-va)
    return None
if exp_rva:
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
    print("exports:", nnames)
    for n in names[:40]: print("  ", n)
else:
    print("NO export directory")
