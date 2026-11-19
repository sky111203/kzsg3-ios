import re
t = open(r"D:\dsh\kzsg3_port\compile_errors.log", encoding="utf-8", errors="replace").read()
blocks = re.split(r"==== (D:[^\n]+)", t)
total = 0
for j in range(1, len(blocks), 2):
    p, body = blocks[j], blocks[j+1]
    errs = [l for l in body.splitlines() if ": error:" in l or "fatal error:" in l]
    if errs:
        total += len(errs)
        print("=====", p.replace("D:/dsh/kzsg3_port/enginejs/cocos2d-js-v3.0-beta/frameworks/js-bindings/", ""), len(errs))
        for e in errs[:5]:
            print("   ", e[-170:])
print("TOTAL error lines:", total)
