import re
t = open(r"D:\dsh\kzsg3_port\compile_errors.log", encoding="utf-8", errors="replace").read()
lines = [l for l in t.splitlines() if "error:" in l]
print("lines containing 'error:':", len(lines))
for l in lines[:25]:
    print(l[-200:])
