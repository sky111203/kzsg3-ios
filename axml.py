# Parse AndroidManifest.xml (binary AXML) for package/version using minimal parser
import struct
d = open(r"D:\dsh\kzsg3_port\apk_extracted\AndroidManifest.xml","rb").read()
def u16(o): return struct.unpack_from("<H", d, o)[0]
def u32(o): return struct.unpack_from("<I", d, o)[0]
# string pool
sp = u32(8+8)  # after header chunk: find string pool
# walk chunks: file header 8 bytes; then chunks
o = 8
types = []
while o < len(d)-8:
    t, hs, sz = struct.unpack_from("<HHI", d, o)
    types.append((hex(t), hs, sz, hex(o)))
    o += sz
for t in types[:10]: print("chunk", t)
