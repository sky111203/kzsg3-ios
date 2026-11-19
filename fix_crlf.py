# -*- coding: utf-8 -*-
p = r"D:\dsh\kzsg3_port\ios_port\tools\tbd_merge.py"
t = open(p, encoding="utf-8").read()
old = 'f.write((' + chr(34) + chr(92) + 'n' + chr(34) + '.join(body) + ' + chr(34) + chr(92) + 'n' + chr(34) + ').encode(' + chr(34) + 'utf-8' + chr(34) + '))'
new = 'f.write((' + chr(34) + chr(92) + 'r' + chr(92) + 'n' + chr(34) + '.join(body) + ' + chr(34) + chr(92) + 'r' + chr(92) + 'n' + chr(34) + ').encode(' + chr(34) + 'utf-8' + chr(34) + '))'
assert old in t, "tbd_merge write pattern missing"
t = t.replace(old, new)
open(p, "w", encoding="utf-8").write(t)
print("tbd_merge CRLF patched")

p2 = r"D:\dsh\kzsg3_port\ios_port\tools\link_ipa.py"
t2 = open(p2, encoding="utf-8").read()
old2 = 'f.write((' + chr(34) + chr(92) + 'n' + chr(34) + '.join(body) + ' + chr(34) + chr(92) + 'n' + chr(34) + ').encode(' + chr(34) + 'utf-8' + chr(34) + '))'
assert old2 in t2, "link stub write pattern missing"
t2 = t2.replace(old2, new)
open(p2, "w", encoding="utf-8").write(t2)
print("auto-tbd CRLF patched")
