import struct
data = open(r"D:\dsh\kzsg3_port\apk_extracted\lib\armeabi\libcocos2dx.so","rb").read()
# dynsym 0x148 size 0x63770, dynstr 0x638b8
symoff, symsz = 0x148, 0x63770
stroff = 0x638b8
def name(x):
    e = data.index(b"\x00", stroff+x)
    return data[stroff+x:e].decode()
want = ["JS_DecodeScript", "JS_CompileScript", "JS_CompileUTF8File", "JS_XDR", "js_XDRScript", "JS_EncodeScript", "xxtea", "XXTEA", "jsb_set", "JSBCore", "JSBCore_start", "runScript", "compileScript", "getScript", "setXXTEAKey"]
found = {}
for i in range(symsz//16):
    o = symoff + i*16
    nameoff, value, sz2, info, other, shndx = struct.unpack_from("<IIIBBH", data, o)
    n = name(nameoff)
    for w in want:
        if w.lower() in n.lower():
            found.setdefault(w, []).append((n, hex(value), sz2, hex(info)))
for w, lst in found.items():
    print("====", w)
    for n, v, s, inf in lst[:10]:
        print(f"   {n:60s} val={v} size={s} info={inf}")
