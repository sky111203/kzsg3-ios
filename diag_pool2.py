import struct
data = open(r"D:\dsh\kzsg3_port\apk_extracted\lib\armeabi\libcocos2dx.so","rb").read()
def lit(pc_addr, imm):
    base = (pc_addr + 4) & ~3
    la = base + imm
    return struct.unpack_from("<I", data, la)[0], la
# string1: ldr r0,[pc,#0x90] @0x39C09C ( Thumb: base=(0x39C09C+4)&~3 )
a1, la1 = lit(0x39C09C, 0x90)
# add r0, pc @0x39C09E -> r0 = a1 + (0x39C09E + 4)
r0 = a1 + 0x39C09E + 4
a2, la2 = lit(0x39C0A0, 0x90)
r1 = (a2 + r0) & 0xFFFFFFFF
print("str1 va:", hex(r1))
e = data.index(b"\x00", r1)
print("str1:", data[r1:r1+80])
# second call strings: ldr r1,[pc,#0x78] @0x39C0BE (r7=page), pattern: r7 = lit(0x39C0BE+4?) ...
# 0x39C0BE: ldr r7,[pc,#0x78] -> r7 = lit value; 0x39C0C0: add r7,pc -> r7 += 0x39C0C0+4
# 0x39C0C2: ldr r0,[pc,#0x78] -> r0 = lit; 0x39C0C4: adds r3, r0, r7 -> r3 = r0 + r7 (page base + off)
a3, _ = lit(0x39C0BE, 0x78)
r7 = a3 + 0x39C0C0 + 4
a4, _ = lit(0x39C0C2, 0x78)
r3 = (a4 + r7) & 0xFFFFFFFF
print("page base:", hex(r7), "arg3 va:", hex(r3))
print("arg3:", data[r3:r3+60])
# the two strings passed to 0x3910bc (2nd args r0=sp+0x18 out, r1=cx, r2=global, r3=str) -> read str at r3
# 2nd pair: ldr r0,[pc,#0x58] @0x39C0EE; ldr r0,[pc,#0x40] @0x39C108 etc
a5, _ = lit(0x39C0EE, 0x58)
r3b = (a5 + r7) & 0xFFFFFFFF
print("arg3b va:", hex(r3b))
print("arg3b:", data[r3b:r3b+60])
a6, _ = lit(0x39C108, 0x40)
r3c = (a6 + r7) & 0xFFFFFFFF
print("arg3c va:", hex(r3c))
print("arg3c:", data[r3c:r3c+60])
