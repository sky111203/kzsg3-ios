import re
t = open(r"D:\dsh\kzsg3_port\compile_errors.log", encoding="utf-8", errors="replace").read()
i = t.find("KZCrashHandler.mm")
print(t[i:i+900])
