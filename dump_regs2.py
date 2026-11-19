import struct, re
data = open(r"D:\dsh\kzsg3_port\apk_extracted\lib\armeabi\libcocos2dx.so","rb").read()
symoff, symsz, stroff = 0x148, 0x63770, 0x638b8
names = []
for i in range(symsz//16):
    o = symoff + i*16
    nameoff, value, sz2, info, other, shndx = struct.unpack_from("<IIIBBH", data, o)
    e = data.index(b"\x00", stroff+nameoff)
    n = data[stroff+nameoff:e].decode()
    if n: names.append((n, value))
regs = sorted(set(n for n,v in names if "register_all" in n or "register_cocos2dx_js" in n or n.startswith("jsb_register")))
print("== register_all/jsb_register count:", len(regs))
for n in regs: print("  ", n)
print()
fams = {}
for n,v in names:
    m = re.match(r"js_(cocos2dx[a-zA-Z0-9_]*)_([A-Za-z_])", n)
    if m: fams[m.group(1)] = fams.get(m.group(1), 0) + 1
print("== js_cocos2dx* symbol families:")
for k,v in sorted(fams.items()): print(f"   {k}: {v}")
