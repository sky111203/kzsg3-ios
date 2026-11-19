import struct, re
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
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
def dis(tag, start, size):
    print("="*16, tag, hex(start))
    for ins in md.disasm(data[start:start+size], start):
        note = ""
        if ins.mnemonic in ("bl","b","blx") and ins.op_str.startswith("#"):
            t = int(ins.op_str[1:],16)
            if t in syms: note = "   ; " + syms[t]
        print(f"{ins.address:08X}: {ins.mnemonic}\t{ins.op_str}{note}")
# JS_DecodeScript definition (thumb addr 0x3c51e0)
dis("JS_DecodeScript", 0x3c51e0, 84)
# wrapper at 0x6636d8
dis("wrapper_6636d8", 0x6636d8, 60)
dis("fn_6636c4", 0x6636c4, 20)
