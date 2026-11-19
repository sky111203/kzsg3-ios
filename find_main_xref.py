import struct
data = open(r"D:\dsh\kzsg3_port\apk_extracted\lib\armeabi\libcocos2dx.so","rb").read()
# ELF32 parse
e_phoff = struct.unpack_from("<I", data, 0x1C)[0]
e_phentsize = struct.unpack_from("<H", data, 0x2A)[0]
e_phnum = struct.unpack_from("<H", data, 0x2C)[0]
segs = []
for i in range(e_phnum):
    off = e_phoff + i*e_phentsize
    p_type, p_offset, p_vaddr, _pa, p_filesz = struct.unpack_from("<IIIII", data, off)
    if p_type == 1:
        segs.append((p_offset, p_vaddr, p_filesz))
        print(f"LOAD off={p_offset:#x} vaddr={p_vaddr:#x} size={p_filesz:#x}")
def off2va(o):
    for po, pv, sz in segs:
        if po <= o < po+sz: return pv + (o - po)
    return None
def va2off(v):
    for po, pv, sz in segs:
        if pv <= v < pv+sz: return po + (v - pv)
    return None
# find "main.js" and neighbors
idx = 0
locs = []
while True:
    i = data.find(b"main.js", idx)
    if i == -1: break
    va = off2va(i)
    print(f"main.js at file {i:#x} va {va:#x} context: {data[max(0,i-40):i+20]}")
    locs.append((i, va))
    idx = i + 1
# scan literal pool references
for i, va in locs:
    vab = struct.pack("<I", va)
    j = 0
    refs = []
    while True:
        k = data.find(vab, j)
        if k == -1: break
        refs.append(k)
        j = k+1
    print(f"refs to va {va:#x}:", [hex(r) for r in refs[:10]], "count", len(refs))
