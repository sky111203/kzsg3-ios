import re
data = open(r"D:\dsh\kzsg3_port\apk_extracted\lib\armeabi\libcocos2dx.so","rb").read()
strs = re.findall(rb"[\x20-\x7e]{4,}", data)
ver = set(); entry = set(); misc = set()
for s in strs:
    t = s.decode(errors="replace")
    if re.search(r"3\.\d+\.\d+", t) and len(t) < 60:
        ver.add(t)
    if "main.js" in t.lower() or "main.jsc" in t.lower() or "config.json" in t.lower() or "jsb-adapter" in t.lower():
        entry.add(t)
    if any(k in t for k in ("jscompile", "XXTEAKey", "xxteaKey", "setKey", "getKey", "encryptKey", "KeyAndBinary")):
        misc.add(t)
print("== VERSION strings:")
for t in sorted(ver)[:60]: print("  ", t)
print("== ENTRY strings:")
for t in sorted(entry)[:40]: print("  ", t)
print("== KEY strings:")
for t in sorted(misc)[:40]: print("  ", t)
