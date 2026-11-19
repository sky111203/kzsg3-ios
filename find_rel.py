import struct
data = open(r"D:\dsh\kzsg3_port\apk_extracted\lib\armeabi\libcocos2dx.so","rb").read()
e_shoff = struct.unpack_from("<I", data, 0x20)[0]
e_shentsize = struct.unpack_from("<H", data, 0x2E)[0]
e_shnum = struct.unpack_from("<H", data, 0x30)[0]
e_shstrndx = struct.unpack_from("<H", data, 0x32)[0]
print("shoff", hex(e_shoff), "shnum", e_shnum)
if e_shoff == 0:
    print("section headers stripped; use dynamic segment")
    e_phoff = struct.unpack_from("<I", data, 0x1C)[0]
    e_phentsize = struct.unpack_from("<H", data, 0x2A)[0]
    e_phnum = struct.unpack_from("<H", data, 0x2C)[0]
    dyn = None
    for i in range(e_phnum):
        off = e_phoff + i*e_phentsize
        p_type, p_offset, p_vaddr, _pa, p_filesz, p_memsz = struct.unpack_from("<IIIIII", data, off)
        if p_type == 2:
            dyn = (p_offset, p_filesz)
    print("PT_DYNAMIC", [hex(x) for x in dyn] if dyn else None)
    o, sz = dyn
    tags = {}
    i = o
    while i < o + sz:
        t, v = struct.unpack_from("<II", data, i)
        if t == 0: break
        tags.setdefault(t, []).append(v)
        i += 8
    # DT_RELA=7 size=8 total=8, DT_REL=17, DT_RELASZ=8, DT_RELsz=18
    for t in (17, 7):
        if t in tags:
            print("DT_REL" if t==17 else "DT_RELA", hex(tags[t][0]), "sz", hex(tags[t+1][0]))
    rel_off = tags.get(17, [(0,0)])[0]
    rel_sz = tags.get(18, [0])[0]
    entries = []
    for i in range(rel_off, rel_off+rel_sz, 8):
        info, off2 = struct.unpack_from("<II", data, i)  # r_info, r_offset? actually r_offset first
    # correct: Elf32_Rel = r_offset, r_info
    cnt = 0
    target = 0xb4d72f
    rels = []
    for i in range(rel_off, rel_off+rel_sz, 8):
        r_offset, r_info = struct.unpack_from("<II", data, i)
        # addend is stored at r_offset in place for REL
        if r_offset < len(data):
            addend = struct.unpack_from("<I", data, r_offset)[0] if r_offset+4<=len(data) else 0
            if addend == target:
                rels.append((r_offset, r_info))
        cnt += 1
    print("total rels:", cnt, "refs to main.js:", [(hex(a), hex(b)) for a,b in rels[:20]])
