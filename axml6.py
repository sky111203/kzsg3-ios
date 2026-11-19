import struct
d = open(r"D:\dsh\kzsg3_port\apk_extracted\AndroidManifest.xml","rb").read()
sp = 8
hs = struct.unpack_from("<H", d, sp+4)[0]
scnt = struct.unpack_from("<I", d, sp+12)[0]
flags = struct.unpack_from("<I", d, sp+16)[0]
sstart = struct.unpack_from("<I", d, sp+20)[0]
print("hs", hs, "scnt", scnt, "flags", hex(flags), "sstart", sstart)
is_utf8 = bool(flags & 0x100)
for i in range(min(scnt, 60)):
    off = sp + sstart + struct.unpack_from("<I", d, sp + hs + i*4)[0]
    if is_utf8:
        n2 = struct.unpack_from("<H", d, off+2)[0]
        s = d[off+4:off+4+n2].decode("utf-8","replace")
    else:
        l = struct.unpack_from("<H", d, off)[0]
        s = d[off+2:off+2+l*2].decode("utf-16le","replace")
    print(i, repr(s[:60]))
