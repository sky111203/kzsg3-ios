import re, struct
data = open(r"D:\dsh\kzsg3_port\apk_extracted\lib\armeabi\libcocos2dx.so","rb").read()
# find XXTEA delta constant occurrences (both endian)
delta = struct.pack("<I", 0x9E3779B9)
pos = []
i = data.find(delta)
while i != -1:
    pos.append(i)
    i = data.find(delta, i+1)
print("DELTA hits (LE):", len(pos), pos[:20])
# find magic 42C073B9 as literal
mag = bytes([0x42,0xC0,0x73,0xB9])
pos2 = []
i = data.find(mag)
while i != -1:
    pos2.append(i)
    i = data.find(mag, i+1)
print("MAGIC hits:", len(pos2), pos2[:20])
# also look for reversed/other-endian delta
delta_be = struct.pack(">I", 0x9E3779B9)
i = data.find(delta_be)
print("DELTA BE hit:", i)
