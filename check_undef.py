import struct
p = r"D:\dsh\kzsg3_port\out\KZSG3"
d = open(p, "rb").read()
magic, cputype, cpusub, filetype, ncmds = struct.unpack_from("<IIIII", d, 0)
off = 32
symtab_off = symtab_n = None
dysym = None
for i in range(ncmds):
    cmd, size = struct.unpack_from("<II", d, off)
    if cmd == 0x2:  # LC_SYMTAB
        symtab_off, symtab_n, stroff, strsize = struct.unpack_from("<IIII", d, off+8)
    off += size
print("symtab entries:", symtab_n)
nsyms = 0
undef = []
STR = d[stroff:stroff+strsize]
for i in range(symtab_n):
    o = symtab_off + i*16
    n_strx, n_type, n_sect, n_desc, n_value = struct.unpack_from("<IBBHI", d, o)
    if (n_type & 0x0E) == 0:  # undefined
        e = STR.index(b"\x00", n_strx)
        undef.append(STR[n_strx:e].decode("utf-8", "replace"))
print("undefined symbols:", len(undef))
import collections
def bucket(s):
    for pre in ["_OBJC_", "_NS", "_UI", "_CF", "_CA", "_CG", "_AV", "_AU", "objc_", "_Sec", "_CT", "_SC", "_CG", "dispatch_", "NS", "CF"]:
        if s.startswith(pre): return "system/objc"
    return "other"
b = collections.Counter(bucket(s) for s in undef)
print(dict(b))
others = [s for s in undef if bucket(s) == "other"]
print("non-system sample:")
for s in others[:25]: print("   ", s)
