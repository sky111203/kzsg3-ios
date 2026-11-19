# -*- coding: utf-8 -*-
import re

# tbd_merge.py: wrap symbols line
p = r"D:\dsh\kzsg3_port\ios_port\tools\tbd_merge.py"
t = open(p, encoding="utf-8").read()
old = '''    body.append("    symbols:         [ %s ]" % ", ".join("'%s'" % s for s in sorted(syms)))
    if objc_classes:
        body.append("    objc-classes:    [ %s ]" % ", ".join(objc_classes))'''
new = '''    sorted_syms = sorted(syms)
    lines = []
    chunk = 24
    for i in range(0, len(sorted_syms), chunk):
        part = ", ".join("'%s'" % s for s in sorted_syms[i:i+chunk])
        lines.append("                       " + part + ("," if i + chunk < len(sorted_syms) else ""))
    for l in lines:
        body.append(l)
    body.append("    ]")
    if objc_classes:
        oc = sorted(objc_classes)
        olines = []
        for i in range(0, len(oc), 24):
            part = ", ".join(oc[i:i+24])
            olines.append("                       " + part + ("," if i + 24 < len(oc) else ""))
        body.append("    objc-classes:    [ %s ]" % ", ".join(oc))'''
assert old in t, "tbd_merge symbols pattern missing"
t = t.replace(old, new)
open(p, "w", encoding="utf-8").write(t)
print("tbd_merge wrap patched")

# link_ipa.py: wrap stub symbols line
p2 = r"D:\dsh\kzsg3_port\ios_port\tools\link_ipa.py"
t2 = open(p2, encoding="utf-8").read()
import re
m = re.search(r'        "    symbols:              \[ " \+ ", "\.join\(s for s in sorted\(syms\)\) \+ " \],"\n        "    \],', t2)
if m:
    new2 = '''        "    symbols:         [ " + ", ".join(
            "'" + s + "'" for s in sorted(syms)) + " ],"'''
    t2 = t2.replace(m.group(0), new2)
    open(p2, "w", encoding="utf-8").write(t2)
    print("link wrap patched")
else:
    print("link wrap pattern not found — check manually")
