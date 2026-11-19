# -*- coding: utf-8 -*-
"""Diff our binary's undefined imports against iOS 15.6 symbol surface."""
import struct, os, re

BIN = r"D:\dsh\kzsg3_port\out\KZSG3"
SDK15 = r"D:\dsh\kzsg3_port\sdk156"

d = open(BIN, "rb").read()
ncmds = struct.unpack_from("<I", d, 16)[0]
off = 32
dylibs, symtab = [], None
for i in range(ncmds):
    cmd, size = struct.unpack_from("<II", d, off)
    if cmd == 0xC:
        s = struct.unpack_from("<I", d, off+8)[0]
        e = d.index(b"\x00", off+s)
        dylibs.append(d[off+s:e].decode())
    if cmd == 0x2:
        symtab = struct.unpack_from("<IIII", d, off+8)
    off += size
symtab_off, symtab_n, stroff, strsize = symtab
STR = d[stroff:stroff+strsize]
undef = []
for i in range(symtab_n):
    o = symtab_off + i*16
    n_strx, n_type, n_sect, n_desc, n_value = struct.unpack_from("<IBBII", d, o)
    if (n_type & 0x0E) == 0 and n_value == 0 and n_sect == 0:
        e = STR.index(b"\x00", n_strx)
        undef.append(STR[n_strx:e].decode("utf-8", "replace"))
print("load dylibs:", len(dylibs), "undefined imports:", len(undef))

# iOS 15.6 exports: parse all tbds, entries valid for arm64-ios
exports = set()
count = 0
for dp, dn, fn in os.walk(SDK15):
    for f in fn:
        if not f.endswith(".tbd"): continue
        p = os.path.join(dp, f)
        try:
            t = open(p, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        # only if the tbd targets include arm64-ios
        if "arm64-ios" not in t.split("exports")[0][:600]:
            pass  # still scan (some files repeat targets per section)
        # v3 style: - archs: [ arm64 ] / platform: ios, then symbols: [ unquoted ]
        for m in re.finditer(r'- archs:\s*\[[^\]]*arm64[^\]]*\]\s*\n\s*symbols:\s*\[(.*?)\]', t, re.S):
            for s2 in m.group(1).split(","):
                s2 = s2.strip()
                if s2 and not s2.startswith("$ld$"):
                    exports.add(s2)
        # v3/v4 文件里的 objc-classes 独立块（同 frameworks 目录所有文件都扫）
        for mm in re.finditer(r'objc-classes:\s*\[(.*?)\]', t, re.S):
            for s in re.findall(r"'([^']+)'", mm.group(1)):
                exports.add("_OBJC_CLASS_$_" + s)
                exports.add("_OBJC_METACLASS_$_" + s)
        for mm in re.finditer(r'objc-classes:\s*\[(.*?)\]', t, re.S):
            for s in mm.group(1).split(","):
                s = s.strip()
                if s and not s.startswith("$ld$"):
                    exports.add("_OBJC_CLASS_$_" + s)
                    exports.add("_OBJC_METACLASS_$_" + s)
        for m in re.finditer(r'- targets:\s*\[[^\]]*arm64-ios[^\]]*\]\s*\n\s*symbols:\s*\[(.*?)\]', t, re.S):
            grp = m.group(1)
            quoted = re.findall(r"'([^']+)'", grp)
            if quoted:
                for s in quoted:
                    if not s.startswith("$ld$"):
                        exports.add(s)
            else:
                for s2 in grp.split(","):
                    s2 = s2.strip()
                    if s2 and not s2.startswith("$ld$"):
                        exports.add(s2)
        # v5 style class lists
        for m in re.finditer(r'objc-classes:\s*\[(.*?)\]', t, re.S):
            for s in re.findall(r"'([^']+)'", m.group(1)):
                exports.add("_OBJC_CLASS_$_" + s)
                exports.add("_OBJC_METACLASS_$_" + s)
        count += 1
print("tbds scanned:", count, "ios15.6 exports:", len(exports))

missing = [s for s in undef if s not in exports]
print("MISSING on iOS15.6:", len(missing))
for s in sorted(missing):
    print("   ", s)
