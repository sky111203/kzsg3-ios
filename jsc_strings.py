import re
for name in [r"main.jsc", r"src\MainUi.jsc", r"script\jsb_cocos2d.jsc"]:
    p = r"D:\dsh\kzsg3_port\apk_extracted\assets" + "\\" + name
    d = open(p,"rb").read()
    strs = re.findall(rb"[\x20-\x7e]{6,}", d)
    print("=====", name, len(d), "bytes,", len(strs), "strings")
    seen = []
    for s in strs:
        t = s.decode()
        if t not in seen:
            seen.append(t)
    for t in seen[:60]:
        print("   ", t)
    print()
