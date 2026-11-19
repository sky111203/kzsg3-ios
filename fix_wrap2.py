# -*- coding: utf-8 -*-
p = r"D:\dsh\kzsg3_port\ios_port\tools\link_ipa.py"
t = open(p, encoding="utf-8").read()
old = '        "    symbols:              [ " + ", ".join(s for s in sorted(syms)) + " ],"'
new = ('        "    symbols:         [ " + ", ".join(\n'
       '            "\'" + s + "\'" for s in sorted(syms)) + " ],"')
assert old in t
t = t.replace(old, new)
open(p, "w", encoding="utf-8").write(t)
import ast
ast.parse(t)
print("link wrap patched + syntax OK")
