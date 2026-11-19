# -*- coding: utf-8 -*-
# 去掉 stub/tbd_merge 输出符号的单引号(v3 tbd 原生格式)

p = r"D:\dsh\kzsg3_port\ios_port\tools\tbd_merge.py"
t = open(p, encoding="utf-8").read()
old = 'pend("    symbols:              [ %s ]" % ", ".join("\'%s\'" % s for s in sorted(syms)))'
new = 'pend("    symbols:              [ %s ]" % ", ".join(s for s in sorted(syms)))'
assert old in t, "tbd_merge pattern missing"
t = t.replace(old, new)
open(p, "w", encoding="utf-8").write(t)
print("tbd_merge patched")

p2 = r"D:\dsh\kzsg3_port\ios_port\tools\link_ipa.py"
t2 = open(p2, encoding="utf-8").read()
old2 = '    symbols:              [ " + ", ".join("\'%s\'" % s for s in sorted(syms)) + " ],'
assert old2 in t2, "link pattern missing"
t2 = t2.replace(old2, '    symbols:              [ " + ", ".join(s for s in sorted(syms)) + " ],')
open(p2, "w", encoding="utf-8").write(t2)
print("link patched")
