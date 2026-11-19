import struct
d = open(r"D:\dsh\kzsg3_port\out\KZSG3", "rb").read()
ncmds = struct.unpack_from("<I", d, 16)[0]
sizeofcmds = struct.unpack_from("<I", d, 20)[0]
print("ncmds", ncmds, "sizeofcmds", sizeofcmds)
off = 32
END = 32 + sizeofcmds
kinds = {0xC:"LOAD_DYLIB", 0x18:"LOAD_WEAK_DYLIB", 0x21:"DYLD_INFO", 0x22:"DYLD_INFO_ONLY",
         0x80000034:"DYLD_CHAINED_FIXUPS", 0x80000035:"DYLD_EXPORTS_TRIE", 0x28:"MAIN",
         0x26:"FUNCTION_STARTS", 0x1B:"DYSYMTAB", 0x19:"SEGMENT_64", 0x1C:"SYMTAB",
         0x1D:"THREAD", 0x29:"UUID", 0x2A:"VERSION_MIN?", 0x25:"DYSYM?", 0x33:"BUILD_VERSION",
         0x32:"MIN_VERSION?", 0x34:"SOURCE_VERSION", 0x2E:"ID_DYLIB", 0x80000022:"REEXPORT_DYLIB", 0x18|0x80000000:"LOAD_WEAK"}
rows = []
while off < END:
    cmd, size = struct.unpack_from("<II", d, off)
    rows.append((cmd, size, off))
    off += size
for cmd, size, o in rows:
    print(f"{o:6d}  cmd=0x{cmd:08X} {kinds.get(cmd,'?'):22s} size={size}")
