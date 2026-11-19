# -*- coding: utf-8 -*-
"""Map crash imageOffsets to nearest symbols in the KZSG3 binary symtab."""
import struct

BIN = r"D:\dsh\kzsg3_port\out\KZSG3"
OFFSETS = [6848400, 6836200, 6619744, 6487096, 455304, 45316, 42260, 40184]

d = open(BIN, "rb").read()
ncmds = struct.unpack_from("<I", d, 16)[0]
off = 32
symtab_off = symtab_n = stroff = strsize = None
for i in range(ncmds):
    cmd, size = struct.unpack_from("<II", d, off)
    if cmd == 0x2:
        symtab_off, symtab_n, stroff, strsize = struct.unpack_from("<IIII", d, off+8)
    off += size

STR = d[stroff:stroff+strsize]
# defined symbols: n_type & 0x0E == N_SECT (0x0E)
syms = []
for i in range(symtab_n):
    o = symtab_off + i*16
    n_strx, n_type, n_sect, n_desc, n_value = struct.unpack_from("<IBBII", d, o)
    if (n_type & 0x0E) == 0x0E and n_value:
        e = STR.index(b"\x00", n_strx)
        name = STR[n_strx:e].decode("utf-8", "replace")
        syms.append((n_value, name))
syms.sort()
print("defined symbols:", len(syms))

def demangle_short(name):
    return name

for target in OFFSETS:
    # binary search nearest symbol <= target
    lo, hi = 0, len(syms)-1
    best = None
    while lo <= hi:
        mid = (lo+hi)//2
        if syms[mid][0] <= target:
            best = syms[mid]; lo = mid+1
        else:
            hi = mid-1
    if best:
        print("+%8d -> %s + %d" % (target, best[1][:120], target - best[0]))
