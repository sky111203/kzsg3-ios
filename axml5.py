import struct, re
d = open(r"D:\dsh\kzsg3_port\apk_extracted\AndroidManifest.xml","rb").read()
sp = 8
hs = u16 = struct.unpack_from("<H", d, sp+4)[0]
scnt = struct.unpack_from("<I", d, sp+12)[0]
flags = struct.unpack_from("<I", d, sp+16)[0]
sstart = struct.unpack_from("<I", d, sp+20)[0]
is_utf8 = bool(flags & 0x100)
out = []
for i in range(scnt):
    off = sp + sstart + struct.unpack_from("<I", d, sp + hs + i*4)[0]
    if is_utf8:
        n2 = struct.unpack_from("<H", d, off+2)[0]
        out.append(d[off+4:off+4+n2].decode("utf-8","replace"))
    else:
        l = struct.unpack_from("<H", d, off)[0]
        out.append(d[off+2:off+2+l*2].decode("utf-16le","replace"))
for s in out:
    if s and not s.startswith("android") and not s.startswith("http") and "/" not in s and "." in s:
        print(s)
