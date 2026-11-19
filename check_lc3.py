import struct
d = open(r"D:\dsh\kzsg3_port\out\KZSG3", "rb").read()
ncmds = struct.unpack_from("<I", d, 16)[0]
off = 32
dylibs = []
fixups = None
for i in range(ncmds):
    cmd, size = struct.unpack_from("<II", d, off)
    if cmd == 0xC:
        s = struct.unpack_from("<I", d, off+8)[0]
        e = d.index(b"\x00", off+s)
        dylibs.append(d[off+s:e].decode())
    if cmd in (0x22, 0x80000022): fixups = "CLASSIC LC_DYLD_INFO_ONLY"
    if cmd == 0x80000034: fixups = "CHAINED FIXUPS (bad)"
    off += size
print("fixup style:", fixups)
bad = [x for x in dylibs if "CollectionViewCore" in x or "UIUtilities" in x]
print("iOS16-only frameworks in load commands:", bad if bad else "NONE")
for x in dylibs: print("   ", x)
