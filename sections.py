import struct
data = open(r"D:\dsh\kzsg3_port\apk_extracted\lib\armeabi\libcocos2dx.so","rb").read()
e_shoff = struct.unpack_from("<I", data, 0x20)[0]
e_shentsize = struct.unpack_from("<H", data, 0x2E)[0]
e_shnum = struct.unpack_from("<H", data, 0x30)[0]
e_shstrndx = struct.unpack_from("<H", data, 0x32)[0]
sh = []
for i in range(e_shnum):
    o = e_shoff + i*e_shentsize
    name, typ, flags, addr, offset, size, link, info, align, entsize = struct.unpack_from("<10I", data, o)
    sh.append(dict(name=name, typ=typ, addr=addr, offset=offset, size=size, link=link, entsize=entsize))
stroff = sh[e_shstrndx]["offset"]
def nm(x):
    e = data.index(b"\x00", stroff+x)
    return data[stroff+x:e].decode()
for s in sh:
    print(f"{nm(s['name']):18s} typ={s['typ']:2d} addr={s['addr']:08x} off={s['offset']:08x} size={s['size']:08x} ent={s['entsize']}")
