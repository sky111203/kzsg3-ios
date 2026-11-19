from capstone import *
data = open(r"D:\dsh\kzsg3_port\apk_extracted\lib\armeabi\libcocos2dx.so","rb").read()
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.skipdata = False
def dis(name, addr_thumb, size):
    print("="*20, name, hex(addr_thumb))
    addr = addr_thumb & ~1
    code = data[addr:addr+size]
    for ins in md.disasm(code, addr):
        print(f"{ins.address:08X}: {ins.mnemonic}\t{ins.op_str}")
dis("getScript", 0x38bd1d, 280)
dis("compileScript", 0x38be65, 516)
dis("JS_DecodeScript", 0x3c51e1, 84)
