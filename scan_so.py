import re
data = open(r"D:\dsh\kzsg3_port\apk_extracted\lib\armeabi\libcocos2dx.so","rb").read()
strs = re.findall(rb"[\x20-\x7e]{5,}", data)
hits = {}
keys = [b"cocos2d", b"XXTEA", b"xxtea", b"xxteaKey", b"jsb", b"spider", b"Spider", b"JSCScriptingCore", b"ScriptingCore", b"mozjs", b"decrypt", b".jsc", b"version", b"cocos2d-js", b"Cocos2d"]
for s in strs:
    for k in keys:
        if k in s:
            hits.setdefault(k, []).append(s[:120])
for k,v in hits.items():
    print("====", k.decode())
    uniq = []
    for s in v:
        if s not in uniq:
            uniq.append(s)
    for s in uniq[:40]:
        print("   ", s.decode(errors="replace"))
