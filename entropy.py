import math, collections, struct, zlib
p = r"D:\dsh\kzsg3_port\apk_extracted\assets\src\MainUi.jsc"
d = open(p,"rb").read()
def entropy(b):
    c = collections.Counter(b)
    n = len(b)
    return -sum(v/n * math.log2(v/n) for v in c.values())
print("size:", len(d))
print("entropy head 16:", round(entropy(d[:16]),3))
print("entropy body[16:]:", round(entropy(d[16:]),3))
# sample regions
for a,b in [(16,528),(528,1000),(1000,10000),(60000,128000)]:
    if b<=len(d): print(f"entropy[{a}:{b}]=", round(entropy(d[a:b]),3))
# try zlib raw/deflate at offsets 4,8,12,16,17
for off in (4,8,12,16,17,18,20):
    for wbits in (15, -15, 47):
        try:
            r = zlib.decompressobj(wbits).decompress(d[off:], 64)
            if len(r) > 8:
                print("ZLIB OK at", off, "wbits", wbits, r[:40])
        except Exception as e:
            pass
# ASCII ratio
ascii_ct = sum(1 for x in d[16:] if 32<=x<127)
print("ascii ratio body:", round(ascii_ct/len(d[16:]),3))
print("first 64 body hex:", d[16:80].hex(" "))
