import re
p = r"D:\dsh\kzsg3_port\sdk\iPhoneOS16.5.sdk\usr\lib\libSystem.tbd"
t = open(p, encoding="utf-8", errors="replace").read()
print("len:", len(t))
print("has _malloc:", "_malloc" in t)
print("has reexported:", "reexported-libraries" in t)
print("targets:", re.search(r"targets:\s*\[[^\]]*\]", t).group(0)[:120])
i = t.find("exports")
print(t[i:i+500])
