import struct
d = open(r"D:\dsh\kzsg3_port\apk_extracted\AndroidManifest.xml","rb").read()
sp = 8
hs = struct.unpack_from("<H", d, sp+2)[0]
scnt = struct.unpack_from("<I", d, sp+8)[0]
flags = struct.unpack_from("<I", d, sp+16)[0]
sstart = struct.unpack_from("<I", d, sp+20)[0]
is_utf8 = bool(flags & 0x100)
res = []
for i in range(scnt):
    off = sp + sstart + struct.unpack_from("<I", d, sp + hs + i*4)[0]
    if is_utf8:
        n2 = struct.unpack_from("<H", d, off+2)[0]
        s = d[off+4:off+4+n2].decode("utf-8","replace")
    else:
        l = struct.unpack_from("<H", d, off)[0]
        s = d[off+2:off+2+l*2].decode("utf-16le","replace")
    res.append(s)
for s in res:
    if "." in s and "/" not in s and len(s) < 60: print(s)
