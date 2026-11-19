import struct
data = open(r"D:\dsh\kzsg3_port\apk_extracted\lib\armeabi\libcocos2dx.so","rb").read()
# .rel.dyn at 0x1d65e4 size 0x8e970 (addend stored in place)
target = 0xb4d72f  # "main.js"
hits = []
o, sz = 0x1d65e4, 0x8e970
for i in range(o, o+sz, 8):
    r_offset, r_info = struct.unpack_from("<II", data, i)
    if r_offset+4 <= len(data):
        add = struct.unpack_from("<I", data, r_offset)[0]
        if add == target:
            hits.append((r_offset, r_info))
print("main.js refs:", [(hex(a), hex(b)) for a,b in hits])
# also "script/jsb_boot.js" va:
t2 = 0xb4d72f - len("main.js") - 1 - len("script/jsb_boot.js")
print("jsb_boot va:", hex(t2), data[t2:t2+30])
