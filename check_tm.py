# -*- coding: utf-8 -*-
t = open(r"D:\dsh\kzsg3_port\ios_port\tools\tbd_merge.py", encoding="utf-8").read()
print("len:", len(t))
print("has v4 emit:", '"--- !tapi-tbd"' in t)
print("has v3 emit:", "tapi-tbd-v3" in t)
i = t.find("def merge_arm64")
print(t[i:i+200])
