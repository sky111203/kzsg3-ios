import struct
d = open(r"D:\dsh\kzsg3_port\out\KZSG3", "rb").read()
ncmds = struct.unpack_from("<I", d, 16)[0]
off = 32
for i in range(ncmds):
    cmd, size = struct.unpack_from("<II", d, off)
    if cmd == 0x19:
        name = d[off+8:off+24].rstrip(b"\x00").decode()
        print("segment:", name)
    off += size
