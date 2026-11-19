import struct
from capstone import *
data = open(r"D:\dsh\kzsg3_port\apk_extracted\lib\armeabi\libcocos2dx.so","rb").read()
symoff, symsz, stroff = 0x148, 0x63770, 0x638b8
syms = {}
for i in range(symsz//16):
    o = symoff + i*16
    nameoff, value, sz2, info, other, shndx = struct.unpack_from("<IIIBBH", data, o)
    if value:
        e = data.index(b"\x00", stroff+nameoff)
        n = data[stroff+nameoff:e].decode()
        if n: syms[value & ~1] = n
mda = Cs(CS_ARCH_ARM, CS_MODE_ARM)
mda.skipdata = True
out = []
for ins in mda.disasm(data[0x510224:0x510224+2200], 0x510224):
    note = ""
    m = ins.mnemonic + " " + ins.op_str
    import re
    mm = re.match(r"ldr\s+r(\d+), \[pc, #(0x[0-9a-f]+)\]", m)
    if mm:
        la = ((ins.address+8) & ~3) + int(mm.group(2),16)
        if la+4 <= len(data):
            v = struct.unpack_from("<I", data, la)[0]
            note = f"  ; [{la:08X}]={v:08X}"
    if ins.mnemonic == "bl" and ins.op_str.startswith("#"):
        t = int(ins.op_str[1:],16)
        if t in syms: note = "  ; " + syms[t]
    out.append(f"{ins.address:08X}: {m}{note}")
open(r"D:\dsh\kzsg3_port\dis_xdrscript.txt","w", encoding="utf-8").write("\n".join(out))
print("lines:", len(out))
