from capstone import *
import struct
data = open(r"D:\dsh\kzsg3_port\apk_extracted\lib\armeabi\libcocos2dx.so","rb").read()
delta = struct.pack("<I", 0x9E3779B9)
md = Cs(CS_ARCH_ARM, CS_MODE_ARM); md.skipdata = True
hits = []
i = data.find(delta)
while i != -1:
    hits.append(i); i = data.find(delta, i+1)
cand = []
for off in hits:
    if off >= len(data)-200: continue
    code = data[off-160:off+64]
    txt = []
    for ins in md.disasm(code, off-160):
        txt.append(ins.mnemonic + " " + ins.op_str)
    joined = " | ".join(txt)
    # xxtea signature: eor with shifts by 2 and 5, and 3 and 4
    if ("lsl #2" in joined or "lsl r,#2") and ("lsr #5" in joined) and ("lsr #3" in joined) and ("lsl #4" in joined):
        cand.append((off, joined[:400]))
print("xxtea-like functions:", len(cand))
for off, t in cand[:6]:
    print("=== at", hex(off))
    print(t[:800])
    print()
