import os, struct, collections
root = r"D:\dsh\kzsg3_port\apk_extracted\assets"
vers = collections.Counter(); sizes_bad = 0; total = 0
f2f3 = []
for dp, dn, fn in os.walk(root):
    for f in fn:
        if not f.endswith(".jsc"): continue
        p = os.path.join(dp, f)
        d = open(p,"rb").read()
        magic, f1, f2, f3 = struct.unpack_from("<IIII", d[:16])
        ver = struct.unpack_from("<I", d[16:20])[0]
        vers[ver] += 1
        total += 1
        f2f3.append((f, magic, f1, f2, f3, len(d), ver))
print("total:", total)
print("version histogram at offset16:", dict(vers))
print("magic variants:", set(m for _,m,_,_,_,_,_ in f2f3))
print("f1 variants:", set(f1 for _,_,f1,_,_,_,_ in f2f3))
# check f2 vs filesize relationship
for f, m, f1, f2, f3, sz, ver in f2f3[:8]:
    print(f"{f:35s} f2={f2:8d} f3={f3:6d} size={sz:8d} ver={ver}")
# maybe f2 = sum of something; test f2*4?
import statistics
ratios = [sz/max(1,f2) for f,m,f1,f2,f3,sz,v in f2f3]
print("size/f2 ratio min,max:", round(min(ratios),2), round(max(ratios),2))
