import os
root = r"D:\dsh\kzsg3_port\apk_extracted\assets"
files = []
for dp, dn, fn in os.walk(root):
    for f in fn:
        if f.endswith(".jsc"):
            files.append(os.path.join(dp, f))
print("jsc count:", len(files))
import struct
for p in files[:14] + [os.path.join(root,r"src\GameLayer.jsc"), os.path.join(root,r"script\jsb_cocos2d.jsc")]:
    d = open(p,"rb").read(24)
    a, b, c, e = struct.unpack("<IIII", d[:16])
    sz = os.path.getsize(p)
    print(f"{os.path.basename(p):30s} size={sz:8d} magic={a:08X} f1={b:08X} f2={c:08X} f3={e:08X}")
