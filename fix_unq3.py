# -*- coding: utf-8 -*-
p = r"D:\dsh\kzsg3_port\ios_port\tools\link_ipa.py"
t = open(p, encoding="utf-8").read()
old = '''    symbols:              [ " + ", ".join("'%s'" % s for s in sorted(syms)) + " ],'''
new = '''    symbols:              [ " + ", ".join(s for s in sorted(syms)) + " ],'''
assert old in t, "missing"
t = t.replace(old, new)
open(p, "w", encoding="utf-8").write(t)
print("link stub patched")
