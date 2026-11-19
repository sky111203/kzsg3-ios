from capstone import *
data = open(r"D:\dsh\kzsg3_port\apk_extracted\lib\armeabi\libcocos2dx.so","rb").read()
md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
md.skipdata = True
start = 0x50FC00
end   = 0x510600
code = data[start:end]
out = []
for ins in md.disasm(code, start):
    out.append(f"{ins.address:08X}: {ins.mnemonic}\t{ins.op_str}")
open(r"D:\dsh\kzsg3_port\disasm2.txt","w").write("\n".join(out))
print("lines:", len(out))
