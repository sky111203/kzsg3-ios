# -*- coding: utf-8 -*-
p = r"D:\dsh\kzsg3_port\ios_port\tools\link_ipa.py"
t = open(p, encoding="utf-8").read()
t = t.replace('"-error-limit=0"', '"--error-limit=0"')
t = t.replace('"-Wl,-no_uuid", ', '')
open(p, "w", encoding="utf-8").write(t)
print("flags fixed")
