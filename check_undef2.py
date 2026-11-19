import struct, re
p = r"D:\dsh\kzsg3_port\out\KZSG3"
d = open(p, "rb").read()
ncmds = struct.unpack_from("<I", d, 16)[0]
off = 32
for i in range(ncmds):
    cmd, size = struct.unpack_from("<II", d, off)
    if cmd == 0x2:
        symtab_off, symtab_n, stroff, strsize = struct.unpack_from("<IIII", d, off+8)
    off += size
STR = d[stroff:stroff+strsize]
undef = []
for i in range(symtab_n):
    o = symtab_off + i*16
    n_strx, n_type = struct.unpack_from("<IB", d, o)
    if (n_type & 0x0E) == 0:
        e = STR.index(b"\x00", n_strx)
        undef.append(STR[n_strx:e].decode("utf-8", "replace"))
non_std = [s for s in undef if "St3__1" not in s and "St6" not in s and not s.startswith("_ZNSt")]
print("total undefined:", len(undef), "| non-libc++:", len(non_std))
bad = [s for s in undef if ("cocos2d" in s or s.startswith("_Z") and ("2js" in s or "13ScriptingCore" in s))]
print("engine leftovers:", len(bad))
for s in bad[:15]: print("   ", s[:120])
