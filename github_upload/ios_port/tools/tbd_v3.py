# -*- coding: utf-8 -*-
"""Convert a tbd v4 file to a minimal v3 (arm64/ios only) that any lld can parse."""
import re, sys, os

def convert_v4_to_v3(src, dst):
    t = open(src, encoding="utf-8", errors="replace").read()
    def grab(key):
        m = re.search(key + r":\s*'([^']*)'", t)
        return m.group(1) if m else ""
    install_name = grab("install-name")
    cur = grab("current-version") or "0"
    comp = grab("compatibility-version") or "0"
    # collect arm64 symbols from all exports sections
    syms = set()
    # sections look like:  - targets: [ ... arm64-ios ... ] \n    symbols: [ ... ]
    for m in re.finditer(r'- targets:\s*\[[^\]]*arm64-ios[^\]]*\]\s*\n\s*symbols:\s*\[(.*?)\]', t, re.S):
        for s in re.findall(r"'([^']+)'", m.group(1)):
            if s.startswith("$ld$"):
                continue
            syms.add(s)
    # also uuid-less umbrella: some files use "symbols:" directly per target block only
    body = []
    body.append("--- !tapi-tbd")
    body.append("tbd-version:     3")
    body.append("arch:            arm64")
    body.append("platform:        ios")
    body.append("install-name:    '%s'" % install_name)
    body.append("current-version: %s" % cur)
    body.append("compatibility-version: %s" % comp)
    body.append("exported-tbd-flags: [ flat_namespace ]" if False else "")
    body.append("exports:")
    body.append("  - archs:           [ arm64 ]")
    body.append("    symbols:         [ %s ]" % ", ".join("'%s'" % s for s in sorted(syms)))
    out = "\n".join(x for x in body if x != "") + "\n"
    with open(dst, "w", encoding="utf-8") as f:
        f.write(out)
    return len(syms)

if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    n = convert_v4_to_v3(src, dst)
    print("%s -> %s (%d symbols)" % (os.path.basename(src), os.path.basename(dst), n))
