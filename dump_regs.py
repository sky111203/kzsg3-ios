import struct, re
data = open(r"D:\dsh\kzsg3_port\apk_extracted\lib\armeabi\libcocos2dx.so","rb").read()
symoff, symsz, stroff = 0x148, 0x63770, 0x638b8
names = []
for i in range(symsz//16):
    o = symoff + i*16
    nameoff, value, sz2, info, other, shndx = struct.unpack_from("<IIIBBH", data, o)
    e = data.index(b"\x00", stroff+nameoff)
    n = data[stroff+nameoff:e].decode()
    if n: names.append(n)
regs = sorted(set(n for n in names if n.startswith("register_") or n.startswith("js_register") or n.startswith("jsb_register")))
jsgen = sorted(set(n for n in names if re.match(r"js_cocos2dx\w*_", n)))
print("== register* count:", len(regs))
for n in regs: print("  ", n)
print("== js_* families:")
fams = {}
for n in names:
    m = re.match(r"(js_cocos2dx[a-z_]*)_", n)
    if m: fams.setdefault(m.group(1), 0); fams[m.group(1)] += 1
for k,v in sorted(fams.items()): print(f"   {k}: {v}")
open(r"D:\dsh\kzsg3_port\so_registers.txt","w").write("\n".join(regs))
