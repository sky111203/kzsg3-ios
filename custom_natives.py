import re
data = open(r"D:\dsh\kzsg3_port\apk_extracted\lib\armeabi\libcocos2dx.so","rb").read()
strs = set()
for m in re.finditer(rb"[\x20-\x7e]{4,}", data):
    strs.add(m.group(0).decode())
interesting = []
for pat in [r"RequestChannel", r"payCB", r"ResponseChannel", r"kooum", r"KooCocos", r"^Operator$", r"KTPlay", r"koolocal", r"UMeng", r"umeng", r"MobClick", r"tjClick", r"^System$", r"jsb_system", r"appFiles", r"getWritable", r"local storage", r"LocalStorage", r"XMLHttpRequest", r"WebSocket"]:
    hits = [s for s in strs if re.search(pat, s)]
    interesting.append((pat, hits[:6]))
for pat, hits in interesting:
    print("==", pat)
    for h in hits: print("   ", repr(h[:100]))
