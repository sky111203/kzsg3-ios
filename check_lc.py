import struct
d = open(r"D:\dsh\kzsg3_port\out\KZSG3", "rb").read()
ncmds = struct.unpack_from("<I", d, 16)[0]
off = 32
names = {0x21: "LC_DYLD_INFO", 0x22: "LC_DYLD_INFO_ONLY", 0x80000034: "LC_DYLD_CHAINED_FIXUPS",
         0x26: "LC_FUNCTION_STARTS", 0x1D: "LC_LOAD_UPWARD_DYLIB", 0x1B: "LC_DYSYMTAB",
         0x19: "LC_SEGMENT_64", 0x28: "LC_MAIN", 0x1C: "LC_SYMTAB"}
found = []
for i in range(ncmds):
    cmd, size = struct.unpack_from("<II", d, off)
    if cmd in names: found.append(names[cmd])
    off += size
print(found)
