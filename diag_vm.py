import struct
d = open(r"D:\dsh\kzsg3_port\out\KZSG3", "rb").read()
ncmds = struct.unpack_from("<I", d, 16)[0]
off = 32
for i in range(ncmds):
    cmd, size = struct.unpack_from("<II", d, off)
    if cmd == 0x19:
        vmaddr, memsz = struct.unpack_from("<QQ", d, off+8)
        print("first segment vmaddr:", hex(vmaddr), "size:", hex(memsz))
        break
    off += size
