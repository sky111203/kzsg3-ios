# -*- coding: utf-8 -*-
"""Merge multi-document tbd files into one arm64-only v4 tbd lld can parse fully."""
import re

def _collect(doc, syms, objc_classes):
    for mm in re.finditer(r"- targets:\s*\[[^\]]*arm64-ios[^\]]*\]\s*\n\s*symbols:\s*\[(.*?)\]", doc, re.S):
        grp = mm.group(1)
        quoted = re.findall(r"'([^']+)'", grp)
        if quoted:
            for s in quoted:
                if not s.startswith("$ld$"):
                    syms.add(s)
        else:
            for s in grp.split(","):
                s = s.strip()
                if s and not s.startswith("$ld$"):
                    syms.add(s)
    for mm in re.finditer(r"- archs:\s*\[[^\]]*arm64[^\]]*\]\s*\n\s*symbols:\s*\[(.*?)\]", doc, re.S):
        for s in mm.group(1).split(","):
            s = s.strip()
            if s and not s.startswith("$ld$"):
                syms.add(s)
    for mm in re.finditer(r"objc-classes:\s*\[(.*?)\]", doc, re.S):
        foundq = re.findall(r"'([^']+)'", mm.group(1))
        if foundq:
            objc_classes.update(foundq)
        else:
            for s in mm.group(1).split(","):
                s = s.strip()
                if s and not s.startswith('"'):
                    objc_classes.add(s)

def merge_arm64(src, dst, install_override=None):
    t = open(src, encoding="utf-8", errors="replace").read()
    docs = re.split(r"^--- !tapi-tbd(?:-v3)?\s*$", t, flags=re.M)
    install_name, current_version = None, None
    syms, objc_classes = set(), set()
    for doc in docs:
        if not doc.strip():
            continue
        m = re.search(r"install-name:\s*'?([^'\n]+?)'?\s*(?:\n|$)", doc)
        if m and install_name is None:
            install_name = m.group(1)
        m = re.search(r"current-version:\s*(\S+)", doc)
        if m and current_version is None:
            current_version = m.group(1)
        _collect(doc, syms, objc_classes)
    for c in objc_classes:
        syms.add("_OBJC_CLASS_$_" + c)
        syms.add("_OBJC_METACLASS_$_" + c)
    if install_override:
        install_name = install_override
    if not install_name:
        raise ValueError("no install-name in " + src)
    sorted_syms = sorted(syms)
    # 构造符号列表(每行最多 24 个符号, 保持 SDK 风格缩进)
    sym_lines = []
    for i in range(0, len(sorted_syms), 24):
        chunk = sorted_syms[i:i+24]
        prefix = "                       "
        sep = ",\n" if i + 24 < len(sorted_syms) else ""
        sym_lines.append(prefix + ", ".join("'%s'" % s for s in chunk) + sep)
    body = [
        "--- !tapi-tbd",
        "tbd-version:     4",
        "targets:         [ arm64-ios ]",
        "install-name:    '%s'" % install_name,
    ]
    if current_version:
        body.append("current-version: %s" % current_version)
    body.append("exports:")
    body.append("  - targets:         [ arm64-ios ]")
    if sym_lines:
        body.extend("    symbols:         [" + sym_lines[0][0:] if False else "    symbols:         [" + "")
        # 直接内联拼装
        for sl in sym_lines:
            body.append("    " + sl.strip())
    body.append("    ]")
    oc = sorted(objc_classes)
    if oc:
        oc_lines = []
        for i in range(0, len(oc), 24):
            chunk = oc[i:i+24]
            sep = ",\n" if i + 24 < len(oc) else ""
            oc_lines.append("                       " + ", ".join(chunk) + sep)
        body.append("    objc-classes:    [" + "")
        for sl in oc_lines:
            body.append("    " + sl.strip())
        body.append("    ]")
    data = ("\r\n".join(body) + "\r\n").encode("utf-8")
    with open(dst, "wb") as f:
        f.write(data)
    return len(syms)

if __name__ == "__main__":
    import sys
    print(merge_arm64(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None), "symbols merged")
