from capstone import *
data = open(r"D:\dsh\kzsg3_port\apk_extracted\lib\armeabi\libcocos2dx.so","rb").read()
md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
md.detail = False
start = 0x50F000
end   = 0x510600
code = data[start:end]
count = 0
for ins in md.disasm(code, start):
    print(f"{ins.address:08X}: {ins.mnemonic}\t{ins.op_str}")
    count += 1
print("instructions:", count)
