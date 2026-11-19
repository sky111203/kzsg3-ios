# -*- coding: utf-8 -*-
"""Audit: our binary's undefined symbols vs the exports of all 23 linked dylibs (from SDK tbds)."""
import struct, re, os, sys, glob

BIN = r"D:\dsh\kzsg3_port\out\KZSG3"
SDK = r"D:\dsh\kzsg3_port\sdk\iPhoneOS16.5.sdk"

# 1) parse binary: load dylibs + undefined symbols
d = open(BIN, "rb").read()
ncmds = struct.unpack_from("<I", d, 16)[0]
off = 32
dylibs, syminfo = [], {}
for i in range(ncmds):
    cmd, size = struct.unpack_from("<II", d, off)
    if cmd == 0xC:
        s = struct.unpack_from("<I", d, off+8)[0]
        e = d.index(b"\x00", off+s)
        dylibs.append(d[off+s:e].decode())
    syminfo[cmd] = off
    off += size

symtab_off = symtab_n = stroff = strsize = None
off = 32
for i in range(ncmds):
    cmd, size = struct.unpack_from("<II", d, off)
    if cmd == 0x2:
        symtab_off, symtab_n, stroff, strsize = struct.unpack_from("<IIII", d, off+8)
    off += size
STR = d[stroff:stroff+strsize]
undef = []
for i in range(symtab_n):
    o = symtab_off + i*16
    n_strx, n_type = struct.unpack_from("<IB", d, o)
    if (n_type & 0x0E) == 0:
        e = STR.index(b"\x00", n_strx)
        undef.append(STR[n_strx:e].decode("utf-8", "replace"))
print("dylibs:", len(dylibs), "undefined:", len(undef))

# 2) collect exports from the SDK tbds corresponding to load commands + private extras
def tbd_exports(path):
    t = open(path, encoding="utf-8", errors="replace").read()
    syms = set()
    # v4 style:  - targets: [ ... arm64-ios ...] \n symbols: [ ... ]
    for m in re.finditer(r'- targets:\s*\[[^\]]*arm64-ios[^\]]*\]\s*\n\s*symbols:\s*\[(.*?)\]', t, re.S):
        for s in re.findall(r"'([^']+)'", m.group(1)):
            if not s.startswith("$ld$"):
                syms.add(s)
    # v3 style:  - archs: [ arm64 ] \n symbols / objc-classes...
    for m in re.finditer(r'- archs:\s*\[[^\]]*arm64[^\]]*\]\s*\n\s*symbols:\s*\[(.*?)\]', t, re.S):
        for s in re.findall(r"'([^']+)'", m.group(1)):
            syms.add(s)
    # objc-classes / objc-ivars sections (v5)
    for m in re.finditer(r'objc-classes:\s*\[(.*?)\]', t, re.S):
        for s in re.findall(r"'([^']+)'", m.group(1)):
            syms.add("_OBJC_CLASS_$_" + s)
    return syms

export_syms = set()
# map install-name -> tbd path heuristically
candidates = []
for dp, dn, fn in os.walk(os.path.join(SDK, "System", "Library")):
    for f in fn:
        if f.endswith(".tbd"):
            candidates.append(os.path.join(dp, f))
for dp, dn, fn in os.walk(os.path.join(SDK, "usr", "lib")):
    for f in fn:
        if f.endswith(".tbd"):
            candidates.append(os.path.join(dp, f))
loaded_names = [x.split("/")[-1].replace(".framework", "") for x in dylibs]
# link every tbd whose basename matches one of our loaded dylib basenames
matched = 0
for c in candidates:
    base = os.path.splitext(os.path.basename(c))[0]
    t = open(c, encoding="utf-8", errors="replace").read()
    im = re.search(r"install-name:\s*'([^']+)'", t)
    iname = im.group(1) if im else ""
    if iname in dylibs:
        export_syms |= tbd_exports(c)
        matched += 1
print("tbds matched to load commands:", matched, "exported symbols:", len(export_syms))

# 3) our undefineds not covered?
def class_name(s):
    m = re.match(r"_OBJC_CLASS_\$_(.+)", s)
    return m.group(1) if m else None
uncovered = []
for s in undef:
    if s in export_syms:
        continue
    cn = class_name(s)
    if cn and ("_OBJC_CLASS_$_" + cn) in export_syms:
        continue
    # libc++ templates live in libc++.1.dylib (its tbd may not be in sdk usr/lib? check)
    uncovered.append(s)
print("uncovered undefined:", len(uncovered))
# classify uncovered
libcxx = [s for s in uncovered if "St3__1" in s or s.startswith("__Z") and "St3__1" in s]
objc = [s for s in uncovered if s.startswith("_OBJC_")]
other = [s for s in uncovered if s not in libcxx and s not in objc]
print("  libc++ template-ish:", len(libcxx))
print("  objc classes:", len(objc), objc[:12])
print("  other:", len(other))
for s in other[:60]:
    print("    ", s)
