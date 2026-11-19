import struct, os
def a_slices(p):
    d = open(p, "rb").read(4096)
    if d[:8] == b"!<arch>\n":
        # thin archive: read first member - need full scan; simpler: return "ar"
        return None
    if d[:4] in (b"\xcf\xfa\xed\xfe", b"\xce\xfa\xed\xfe"):
        return [struct.unpack_from("<I", d, 4)[0]]
    if d[:4] == b"\xca\xfe\xba\xbe":
        n = struct.unpack_from(">I", d, 4)[0]
        out = []
        for i in range(min(n, 8)):
            off = 8 + i*20
            cputype = struct.unpack_from(">I", d, off+4)[0]
            out.append(cputype)
        return out
    return "unknown"
CPU = {0x0100000C: "arm64", 12: "armv7", 11: "armv7s", 7: "x86", 0x01000007: "x86_64", 9: "arm"}
root = r"D:\dsh\kzsg3_port\enginejs\cocos2d-js-v3.0-beta\frameworks\js-bindings"
for dp, dn, fn in os.walk(root):
    for f in fn:
        if f.endswith(".a"):
            p = os.path.join(dp, f)
            sz = os.path.getsize(p)
            print(f"{sz:>10}  {os.path.relpath(p, root)}")
            if f.endswith("arm64.a") or sz > 2000000:
                pass
