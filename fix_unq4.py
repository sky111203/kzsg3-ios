# -*- coding: utf-8 -*-
import re
p = r"D:\dsh\kzsg3_port\ios_port\tools\link_ipa.py"
t = open(p, encoding="utf-8").read()
m = re.search(r'    symbols:[^\n]*sorted\(syms\)[^\n]*', t)
assert m, "no match"
line = m.group(0)
new = '    symbols:              [ " + ", ".join(s for s in sorted(syms)) + " ],'
t = t.replace(line, new)
open(p, "w", encoding="utf-8").write(t)
print("patched:", new)
