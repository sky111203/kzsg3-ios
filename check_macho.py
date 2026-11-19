import struct
p = r"D:\dsh\kzsg3_port\out\KZSG3"
d = open(p, "rb").read()
magic, cputype, cpusub, filetype = struct.unpack_from("<IIII", d, 0)
print("magic: %#x (64-bit=%s)" % (magic, magic == 0xfeedfacf))
print("cputype: %#x (arm64=%s)" % (cputype, cputype == 0x0100000C))
print("filetype:", filetype, "(MH_EXECUTE=2)" if filetype == 2 else "")
ncmds, sizeof = struct.unpack_from("<II", d, 16)
print("load commands:", ncmds, "sizeof:", sizeof, "filesize:", len(d))
# walk load commands
off = 32
dylibs = []
undefineds_flags = None
for i in range(ncmds):
    cmd, size = struct.unpack_from("<II", d, off)
    if cmd == 0xC:  # LC_LOAD_DYLIB
        s = struct.unpack_from("<I", d, off+8)[0]  # name offset
        end = d.index(b"\x00", off+s)
        dylibs.append(d[off+s:end].decode())
    if cmd == 0x1D: undefineds_flags = "LC_UNDEFINED? "
    off += size
print("== LC_LOAD_DYLIB (%d):" % len(dylibs))
for x in dylibs: print("   ", x)
