import struct, re
data = open(r"D:\dsh\kzsg3_port\apk_extracted\lib\armeabi\libcocos2dx.so","rb").read()
# dump printable strings in region after the function
region = data[0x39C11C:0x39C400]
for m in re.finditer(rb"[\x20-\x7e]{4,}", region):
    print(hex(0x39C11C + m.start()), m.group(0).decode()[:80])
# also decode pool pointer chains: literals around 0x39c1xx hold (pc-rel offsets)
# simpler: find "require"-like path strings anywhere near 0x39c000-0x39c400 done above.
