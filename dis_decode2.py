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
def dis(tag, start, size, md):
    print("="*16, tag, hex(start))
    for ins in md.disasm(data[start:start+size], start):
        note = ""
        m = ins.mnemonic + " " + ins.op_str
        if ins.mnemonic in ("bl","b") and ins.op_str.startswith("#"):
            t = int(ins.op_str[1:],16)
            if t in syms: note = "   ; " + syms[t]
        elif ins.mnemonic == "ldr" and "[pc," in ins.op_str:
            mm = re.match(r"ldr\s+r(\d+), \[pc, #(0x[0-9a-f]+)\]", m)
            if mm:
                la = ((ins.address+8) & ~3) + int(mm.group(2),16)
                v = struct.unpack_from("<I", data, la)[0]
                note = f"   ; [{la:08X}]={v:08X}"
        print(f"{ins.address:08X}: {m}{note}")
import re
dis("JS_DecodeScript ARM", 0x3c51e0, 84, mda)
dis("wrapper6636d8 ARM", 0x6636d8, 80, mda)
