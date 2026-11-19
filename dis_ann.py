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
        if n:
            syms[value & ~1] = n
# demangle-lite: keep as is
def sym(a):
    return syms.get(a & ~1, "?")
# rodata range for string resolve
RO=0xb4d6f0; RO_END=RO+0x1209e8
def rostr(va):
    if RO <= va < RO_END:
        e = data.index(b"\x00", va)
        s = data[va:e]
        if len(s) < 80 and all(32<=b<127 for b in s):
            return s.decode()
    return None
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
def dis(name, addr_thumb, size):
    print("="*24, name, hex(addr_thumb))
    addr = addr_thumb & ~1
    code = data[addr:addr+size]
    ins_list = list(md.disasm(code, addr))
    for idx, ins in enumerate(ins_list):
        note = ""
        # resolve bl/b targets
        if ins.mnemonic in ("bl","b","blx","b.w","bl.w") and ins.op_str.startswith("#"):
            t = int(ins.op_str[1:], 16)
            s = sym(t)
            if s != "?": note = "   ; -> " + s
        # literal loads: ldr rX, [pc, #imm]
        m = re.match(r"ldr\s+r(\d+), \[pc, #(0x[0-9a-f]+)\]", ins.mnemonic + " " + ins.op_str)
        if m:
            imm = int(m.group(2), 16)
            base = (ins.address + 4) & ~3
            la = base + imm
            if la+4 <= len(data):
                v = struct.unpack_from("<I", data, la)[0]
                note = f"   ; [{la:08X}]={v:08X}"
                # pc-relative add follows? check next few ins for 'add rX, pc'
                for j in range(idx+1, min(idx+4, len(ins_list))):
                    ni = ins_list[j]
                    if re.match(r"add\sr"+m.group(1)+r",\spc", ni.mnemonic + " " + ni.op_str):
                        eff = ins.address + 4 + v  # pc at add = ldraddr+4? use add addr+4 approx
                        eff2 = ni.address + 4 + v
                        s2 = rostr(eff2)
                        note += f" => {eff2:08X}" + (f' "{s2}"' if s2 else "")
                    if ni.mnemonic.startswith("ldr") and "r" + m.group(1) + "," in ni.op_str and "[" in ni.op_str and "pc" not in ni.op_str and "sp" not in ni.op_str:
                        break
        # direct bl to plt/sym
        print(f"{ins.address:08X}: {ins.mnemonic}\t{ins.op_str}{note}")
dis("compileScript", 0x38be65, 516)
