import struct
data = open(r"D:\dsh\kzsg3_port\apk_extracted\lib\armeabi\libcocos2dx.so","rb").read()
symoff, symsz, stroff = 0x148, 0x63770, 0x638b8
target = None
for i in range(symsz//16):
    o = symoff + i*16
    nameoff, value, sz2, info, other, shndx = struct.unpack_from("<IIIBBH", data, o)
    e = data.index(b"\x00", stroff+nameoff)
    n = data[stroff+nameoff:e].decode()
    if "register_cocos2dx_js_core" in n:
        target = value & ~1
        print("found:", n, hex(value), "size:", sz2)
if target:
    from capstone import *
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    size = 800
    for ins in md.disasm(data[target:target+size], target):
        note = ""
        if ins.mnemonic == "bl" and ins.op_str.startswith("#"):
            t = int(ins.op_str[1:], 16)
            # resolve PLT stubs roughly: print target
            note = "  ; -> %#x" % t
        # JS_DefineFunction takes name as const char* — the string pointer comes from literal loads
        print("%08X: %s %s%s" % (ins.address, ins.mnemonic, ins.op_str, note))
